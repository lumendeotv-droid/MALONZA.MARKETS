from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
import time
import threading
import requests
import uuid
import hmac
import hashlib
from django.conf import settings

# ========== PAYMENT HELPERS ==========

def create_paystack_transaction(email, phone, amount_kes, reference, metadata, callback_url):
    """Initialize Paystack transaction (supports both card and M-Pesa)"""
    amount_in_cents = int(amount_kes * 100)
    
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "email": email,
        "amount": amount_in_cents,
        "currency": "KES",
        "reference": reference,
        "callback_url": callback_url,
        "metadata": metadata
    }
    
    # If phone number is provided, enable mobile money (M-Pesa)
    if phone:
        payload['phone'] = phone
        payload['channels'] = ['mobile_money', 'card']
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def verify_paystack_transaction(reference):
    """Verify Paystack transaction status"""
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    return response.json()

def grant_access_after_payment(user_id, payment_type, item_id):
    """Grant access to course or bot after successful payment"""
    try:
        user = SiteUsers.objects.get(id=user_id)
        if payment_type == 'course':
            course = Course.objects.get(id=item_id)
            UserCourseAccess.objects.get_or_create(user=user, course=course)
            return True
        elif payment_type == 'bot':
            bot = TradingBot.objects.get(id=item_id)
            UserBotAccess.objects.get_or_create(user=user, bot=bot)
            return True
    except Exception as e:
        print(f"Error granting access: {e}")
        return False
    return False

# ========== CORE PAGE VIEWS ==========

def index(request):
    user_id = request.session.get('user_id')
    performance_stats = PerformanceStats.objects.first()
    available_ais_count = TradingBot.objects.filter(is_active=True).count()
    
    context = {
        'hero': HeroSection.objects.first(),
        'about': AboutSection.objects.first(),
        'facts': Fact.objects.all(),
        'features': Feature.objects.all(),
        'services': Service.objects.all(),
        'pricing_plans': PricingPlan.objects.all(),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'brokers': Broker.objects.all(),
        'social_links': SocialLink.objects.all(),
        'settings': SiteSettings.objects.first(),
        'courses': Course.objects.filter(is_active=True),
        'blogs': Blog.objects.filter(is_active=True),
        'user_authenticated': user_id is not None,
        'performance_stats': {
            'overall': performance_stats.overall_win_rate if performance_stats else 78.5,
            'weekly': performance_stats.weekly_win_rate if performance_stats else 82.3,
        },
        'available_ais_count': available_ais_count,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    }
    
    if user_id:
        user = SiteUsers.objects.filter(id=user_id).first()
        if user:
            purchased = UserCourseAccess.objects.filter(user=user).values_list('course_id', flat=True)
            context['purchased_course_ids'] = list(purchased)
        else:
            context['purchased_course_ids'] = []
    else:
        context['purchased_course_ids'] = []
    
    return render(request, 'index.html', context)

def dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user = SiteUsers.objects.get(id=user_id)
    purchased_access = UserCourseAccess.objects.filter(user=user)
    purchased_course_ids = list(purchased_access.values_list('course_id', flat=True))
    purchased_courses_list = Course.objects.filter(id__in=purchased_course_ids)
    
    course_purchases = CoursePayments.objects.filter(userId=user_id, payment_status='completed')
    service_purchases = ServicePayments.objects.filter(userId=user_id, payment_status='completed')
    bot_purchases = BotPayments.objects.filter(userId=user_id, payment_status='completed')
    
    featured_videos = Video.objects.filter(is_active=True)[:3]
    all_videos = Video.objects.filter(is_active=True)
    featured_bots = TradingBot.objects.filter(is_active=True, is_featured=True)[:3]
    all_bots = TradingBot.objects.filter(is_active=True)
    
    context = {
        'user': user,
        'all_courses': Course.objects.filter(is_active=True),
        'purchased_courses': purchased_courses_list,
        'purchased_course_ids': purchased_course_ids,
        'course_purchases': course_purchases,
        'service_purchases': service_purchases,
        'bot_purchases': bot_purchases,
        'downloads_count': purchased_courses_list.count(),
        'featured_videos': featured_videos,
        'all_videos': all_videos,
        'featured_bots': featured_bots,
        'all_bots': all_bots,
    }
    
    return render(request, 'dashboard.html', context)

def update_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': 'Not logged in'})
    
    if request.method == 'POST':
        user = SiteUsers.objects.get(id=user_id)
        user.username = request.POST.get('username', user.username)
        user.phone = request.POST.get('phone', user.phone)
        user.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
        return redirect('/dashboard')
    
    return redirect('/dashboard')

def register(request):
    return render(request, 'register.html')

def login_page(request):
    return render(request, "login.html")

def forgot(request):
    return render(request, "forgot.html")

def create_account(request):
    password1 = request.POST.get('password1', False)
    password = request.POST.get('password', False)
    email = request.POST.get('email', False)
    phone = request.POST.get('phone', False)
    username = request.POST.get('username', False)

    if password1 != password:
        message = "The two passwords are different."
        return render(request, "register.html", {"message": message})

    if not email or not password1:
        message = "Email and password are required."
        return render(request, "register.html", {"message": message})

    if SiteUsers.objects.filter(email=email).exists():
        message = "User with this email already exists."
        return render(request, "register.html", {"message": message})

    user = SiteUsers.objects.create(email=email, password=password1, phone=phone, username=username)
    return redirect("/login")

def auth_login(request):
    email = request.POST.get('email', False)
    password = request.POST.get('password', False)

    if not email or not password:
        message = "Email and password are required."
        return render(request, "login.html", {"message": message})

    try:
        user = SiteUsers.objects.get(email=email)
    except SiteUsers.DoesNotExist:
        message = "User does not exist. Please sign up."
        return render(request, "login.html", {"message": message})

    if user.password != password:
        message = "You provided an incorrect password."
        return render(request, "login.html", {"message": message})

    request.session['user_id'] = user.id
    return redirect('/dashboard')

def logout(request):
    user_id = request.session.get('user_id')
    if user_id is not None:
        del request.session['user_id']
    return redirect("/index")

# ========== SERVICE PAYMENT ==========

def payments(request, amount):
    """Handle service payments (Signals $50, Virtual $500, Elite $750)"""
    user_id = request.session.get('user_id')
    if user_id is not None:
        usdprice = float(amount)
        keprice = int(usdprice * 130)
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['payment_type'] = 'service'
        
        if usdprice == 50:
            service_name = "Signals Package"
        elif usdprice == 500:
            service_name = "Virtual Mentorship"
        elif usdprice == 750:
            service_name = "Elite Mentorship"
        else:
            service_name = f"Service (${usdprice})"
        
        request.session['service_name'] = service_name
        
        return render(request, "payment.html", {
            "usdprice": usdprice,
            "keprice": keprice,
            "item_name": service_name,
            "item_type": "service",
            "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        })
    else:
        return redirect("/login")

# ========== COURSE PAYMENT ==========

def coursepayments(request, amount, course_id):
    """Handle course payments"""
    user_id = request.session.get('user_id')
    if user_id is not None:
        usdprice = float(amount)
        keprice = int(usdprice * 130)
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['courseId'] = course_id
        request.session['payment_type'] = 'course'
        
        course = Course.objects.get(id=course_id)
        request.session['course_title'] = course.title
        
        return render(request, "payment.html", {
            "usdprice": usdprice,
            "keprice": keprice,
            "item_name": course.title,
            "item_type": "course",
            "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        })
    else:
        return redirect("/login")

# ========== BOT PAYMENT ==========

def bot_payments(request, bot_id):
    """Handle bot/AI payments"""
    user_id = request.session.get('user_id')
    if user_id is not None:
        bot = TradingBot.objects.get(id=bot_id, is_active=True)
        usdprice = float(bot.price)
        keprice = int(usdprice * 130)
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['botId'] = bot_id
        request.session['payment_type'] = 'bot'
        request.session['bot_name'] = bot.name
        
        return render(request, "payment.html", {
            "usdprice": usdprice,
            "keprice": keprice,
            "item_name": bot.name,
            "item_type": "bot",
            "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY,
        })
    else:
        return redirect("/login")

# ========== PAYSTACK INITIALIZE ==========

@csrf_exempt
def paystack_initialize(request):
    """Initialize Paystack payment - works for services, courses, and bots"""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not logged in', 'redirect': '/login'}, status=401)
        
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        
        if phone:
            phone = phone.strip()
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif phone.startswith('+'):
                phone = phone[1:]
        
        user = SiteUsers.objects.get(id=user_id)
        if not email:
            email = user.email
        
        amount_kes = int(request.session.get('keprice', 0))
        if amount_kes <= 0:
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        payment_type = request.session.get('payment_type', 'service')
        reference = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        request.session['paystack_reference'] = reference
        
        metadata = {
            'user_id': user_id,
            'payment_type': payment_type,
            'user_email': email,
            'amount_usd': str(request.session.get('usdprice', 0)),
            'amount_kes': amount_kes,
            'custom_fields': []
        }
        
        if phone:
            metadata['phone'] = phone
        
        if payment_type == 'service':
            service_name = request.session.get('service_name', 'Service Package')
            metadata['service_name'] = service_name
            metadata['custom_fields'].append({
                'display_name': 'Service',
                'variable_name': 'service',
                'value': service_name
            })
        elif payment_type == 'course':
            course_id = request.session.get('courseId')
            metadata['course_id'] = course_id
            metadata['custom_fields'].append({
                'display_name': 'Course',
                'variable_name': 'course_id',
                'value': str(course_id)
            })
        elif payment_type == 'bot':
            bot_id = request.session.get('botId')
            metadata['bot_id'] = bot_id
            metadata['custom_fields'].append({
                'display_name': 'Trading Bot',
                'variable_name': 'bot_id',
                'value': str(bot_id)
            })
        
        callback_url = request.build_absolute_uri('/paystack/callback/')
        result = create_paystack_transaction(email, phone, amount_kes, reference, metadata, callback_url)
        
        if result.get('status'):
            if payment_type == 'service':
                ServicePayments.objects.create(
                    email=email,
                    phone=phone if phone else None,
                    amountkes=amount_kes,
                    amountusd=request.session.get('usdprice'),
                    service=request.session.get('service_name'),
                    userId=user_id,
                    payment_status='pending',
                    payment_reference=reference,
                    payment_method='paystack'
                )
            elif payment_type == 'course':
                CoursePayments.objects.create(
                    email=email,
                    phone=phone if phone else None,
                    amountkes=amount_kes,
                    amountusd=request.session.get('usdprice'),
                    courseId=request.session.get('courseId'),
                    userId=user_id,
                    payment_status='pending',
                    payment_reference=reference,
                    payment_method='paystack'
                )
            else:
                BotPayments.objects.create(
                    email=email,
                    phone=phone if phone else None,
                    amountkes=amount_kes,
                    amountusd=request.session.get('usdprice'),
                    botId=request.session.get('botId'),
                    userId=user_id,
                    payment_status='pending',
                    payment_reference=reference,
                    payment_method='paystack'
                )
            
            return JsonResponse({
                'status': 'success',
                'authorization_url': result['data']['authorization_url'],
                'reference': reference,
            })
        else:
            return JsonResponse({'error': result.get('message', 'Payment initialization failed')}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# ========== PAYSTACK CALLBACK ==========

def paystack_callback(request):
    """Handle user return after payment"""
    reference = request.GET.get('reference')
    if not reference:
        return redirect('/dashboard?payment=error&message=No+payment+reference')
    
    result = verify_paystack_transaction(reference)
    
    if result.get('status') and result['data']['status'] == 'success':
        data = result['data']
        metadata = data.get('metadata', {})
        user_id = metadata.get('user_id')
        payment_type = metadata.get('payment_type')
        channel = data.get('channel', 'unknown')
        
        if payment_type == 'service':
            payment = ServicePayments.objects.filter(payment_reference=reference).first()
            if payment:
                payment.payment_status = 'completed'
                payment.channel = channel
                payment.save()
        elif payment_type == 'course':
            payment = CoursePayments.objects.filter(payment_reference=reference).first()
            if payment:
                payment.payment_status = 'completed'
                payment.channel = channel
                payment.save()
                if user_id:
                    grant_access_after_payment(user_id, 'course', metadata.get('course_id'))
        elif payment_type == 'bot':
            payment = BotPayments.objects.filter(payment_reference=reference).first()
            if payment:
                payment.payment_status = 'completed'
                payment.channel = channel
                payment.save()
                if user_id:
                    grant_access_after_payment(user_id, 'bot', metadata.get('bot_id'))
        
        request.session.pop('usdprice', None)
        request.session.pop('keprice', None)
        request.session.pop('payment_type', None)
        request.session.pop('courseId', None)
        request.session.pop('botId', None)
        request.session.pop('service_name', None)
        
        return redirect(f'/dashboard?payment=success&reference={reference}&channel={channel}')
    else:
        error_msg = result.get('message', 'Payment verification failed')
        return redirect(f'/dashboard?payment=failed&message={error_msg}')

# ========== PAYSTACK WEBHOOK ==========

@csrf_exempt
def paystack_webhook(request):
    """Paystack webhook for server-to-server confirmation"""
    if request.method == 'POST':
        paystack_signature = request.headers.get('x-paystack-signature')
        if not paystack_signature:
            return HttpResponse(status=401)
        
        secret = settings.PAYSTACK_SECRET_KEY
        body = request.body
        computed_hmac = hmac.new(secret.encode('utf-8'), body, hashlib.sha512).hexdigest()
        
        if not hmac.compare_digest(computed_hmac, paystack_signature):
            return HttpResponse(status=401)
        
        event = json.loads(request.body)
        event_type = event.get('event')
        
        if event_type == 'charge.success':
            data = event['data']
            reference = data['reference']
            metadata = data.get('metadata', {})
            user_id = metadata.get('user_id')
            payment_type = metadata.get('payment_type')
            channel = data.get('channel', 'unknown')
            
            if payment_type == 'service':
                payment = ServicePayments.objects.filter(payment_reference=reference).first()
                if payment and payment.payment_status != 'completed':
                    payment.payment_status = 'completed'
                    payment.channel = channel
                    payment.save()
            elif payment_type == 'course':
                payment = CoursePayments.objects.filter(payment_reference=reference).first()
                if payment and payment.payment_status != 'completed':
                    payment.payment_status = 'completed'
                    payment.channel = channel
                    payment.save()
                    if user_id:
                        grant_access_after_payment(user_id, 'course', metadata.get('course_id'))
            elif payment_type == 'bot':
                payment = BotPayments.objects.filter(payment_reference=reference).first()
                if payment and payment.payment_status != 'completed':
                    payment.payment_status = 'completed'
                    payment.channel = channel
                    payment.save()
                    if user_id:
                        grant_access_after_payment(user_id, 'bot', metadata.get('bot_id'))
            
            print(f"Webhook: {reference} - {payment_type} - {channel}")
        
        return HttpResponse(status=200)
    
    return HttpResponse(status=405)

# ========== LEGACY MPESA CHECKOUT (KEPT FOR COMPATIBILITY) ==========

def mpesa_checkout(request):
    """Legacy M-Pesa checkout simulation"""
    user_id = request.session.get('user_id')
    if user_id is not None:
        phone = request.POST.get('phone', False)
        email = SiteUsers.objects.get(id=user_id).email
        amountkes = request.session.get('keprice')
        usdprice = request.session.get('usdprice')
        payment_type = request.session.get('payment_type')
        
        if phone and phone.startswith('0'):
            phone = '254' + phone[1:]
        
        if payment_type == 'service':
            if usdprice == 50:
                service = "SignalsPackage"
            elif usdprice == 500:
                service = "VirtualMentorshipPlan"
            elif usdprice == 750:
                service = "PhysicalMentorshipPlan"
            else:
                service = "UnknownPlan"
            
            payment_instance = ServicePayments.objects.create(
                mpesa_number=phone, 
                email=email, 
                amountkes=amountkes, 
                service=service, 
                userId=user_id,
                payment_status='pending'
            )
        elif payment_type == 'course':
            courseid = request.session.get('courseId')
            payment_instance = CoursePayments.objects.create(
                mpesa_number=phone,
                email=email,
                amountkes=amountkes,
                courseId=courseid,
                userId=user_id,
                payment_status='pending'
            )
        else:
            bot_id = request.session.get('botId')
            payment_instance = BotPayments.objects.create(
                mpesa_number=phone,
                email=email,
                amountkes=amountkes,
                amountusd=usdprice,
                botId=bot_id,
                userId=user_id,
                payment_status='pending'
            )
        
        payment_instance.save()
        
        def process_payment():
            time.sleep(3)
            payment_instance.payment_status = 'completed'
            payment_instance.save()
            
            if payment_type == 'course':
                user = SiteUsers.objects.get(id=user_id)
                course = Course.objects.get(id=courseid)
                UserCourseAccess.objects.get_or_create(user=user, course=course)
            elif payment_type == 'bot':
                user = SiteUsers.objects.get(id=user_id)
                bot = TradingBot.objects.get(id=bot_id)
                UserBotAccess.objects.get_or_create(user=user, bot=bot)
            
            print(f"Payment of KES {amountkes} received from {phone}")
        
        thread = threading.Thread(target=process_payment)
        thread.start()
        
        return render(request, "loading.html", {"payment_id": payment_instance.id, "payment_type": payment_type})
    else:
        return redirect('/login')

def CardPayments(request):
    """Legacy card payment simulation"""
    user_id = request.session.get('user_id')
    if user_id is not None:
        email = SiteUsers.objects.get(id=user_id).email
        usdprice = request.session.get('usdprice')
        payment_type = request.session.get('payment_type')
        
        if payment_type == 'service':
            if usdprice == 50:
                service = "SignalsPackage"
            elif usdprice == 500:
                service = "VirtualMentorshipPlan"
            elif usdprice == 750:
                service = "PhysicalMentorshipPlan"
            else:
                service = "UnknownPlan"
            
            payment_instance = ServicePayments.objects.create(
                email=email, 
                amountusd=usdprice, 
                service=service, 
                userId=user_id,
                payment_method='card',
                payment_status='pending'
            )
        elif payment_type == 'course':
            courseid = request.session.get('courseId')
            payment_instance = CoursePayments.objects.create(
                email=email,
                amountusd=usdprice,
                courseId=courseid,
                userId=user_id,
                payment_method='card',
                payment_status='pending'
            )
        else:
            bot_id = request.session.get('botId')
            payment_instance = BotPayments.objects.create(
                email=email,
                amountusd=usdprice,
                botId=bot_id,
                userId=user_id,
                payment_method='card',
                payment_status='pending'
            )
        
        payment_instance.save()
        
        def process_card_payment():
            time.sleep(3)
            payment_instance.payment_status = 'completed'
            payment_instance.save()
            
            if payment_type == 'course':
                user = SiteUsers.objects.get(id=user_id)
                course = Course.objects.get(id=courseid)
                UserCourseAccess.objects.get_or_create(user=user, course=course)
            elif payment_type == 'bot':
                user = SiteUsers.objects.get(id=user_id)
                bot = TradingBot.objects.get(id=bot_id)
                UserBotAccess.objects.get_or_create(user=user, bot=bot)
            
            print(f"Card payment of ${usdprice} received from {email}")
        
        thread = threading.Thread(target=process_card_payment)
        thread.start()
        
        return render(request, "loading.html", {"payment_id": payment_instance.id, "payment_type": payment_type})
    else:
        return redirect("/login")

def course_mpesa_checkout(request):
    request.session['payment_type'] = 'course'
    return mpesa_checkout(request)

def course_cardPayments(request):
    request.session['payment_type'] = 'course'
    return CardPayments(request)

def bot_mpesa_checkout(request):
    request.session['payment_type'] = 'bot'
    return mpesa_checkout(request)

def bot_card_payments(request):
    request.session['payment_type'] = 'bot'
    return CardPayments(request)

# ========== PAYMENT STATUS API ==========

@csrf_exempt
def check_payment_status(request):
    payment_id = request.GET.get('payment_id')
    payment_type = request.GET.get('payment_type')
    
    if payment_type == 'service':
        payment = ServicePayments.objects.filter(id=payment_id).first()
    elif payment_type == 'course':
        payment = CoursePayments.objects.filter(id=payment_id).first()
    else:
        payment = BotPayments.objects.filter(id=payment_id).first()
    
    if payment:
        return JsonResponse({
            'status': payment.payment_status,
            'payment_id': payment.id,
            'reference': payment.payment_reference
        })
    return JsonResponse({'status': 'not_found'}, status=404)

# ========== API ENDPOINTS ==========

@csrf_exempt
def subscribe_newsletter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except:
            email = request.POST.get('email')
        
        if email:
            sub, created = NewsletterSubscription.objects.get_or_create(email=email)
            if created:
                return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
            return JsonResponse({'success': False, 'message': 'Already subscribed!'})
    return JsonResponse({'success': False, 'message': 'Invalid email!'})

@csrf_exempt
def submit_contact(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            phone = data.get('phone')
            package = data.get('package')
            message = data.get('message')
        except:
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            package = request.POST.get('package')
            message = request.POST.get('message')
        
        if name and phone and message:
            ContactMessage.objects.create(
                name=name,
                phone=phone,
                package=package,
                message=message
            )
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
    return JsonResponse({'success': False, 'message': 'Invalid request!'})

def get_user_email(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = SiteUsers.objects.filter(id=user_id).first()
        if user:
            return JsonResponse({'email': user.email, 'phone': user.phone or ''})
    return JsonResponse({'email': '', 'phone': ''})