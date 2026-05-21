from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
import time
import threading

def index(request):
    user_id = request.session.get('user_id')
    
    # Get performance stats
    performance_stats = PerformanceStats.objects.first()
    
    # Get available AIs count
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
    purchases = CoursePayments.objects.filter(userId=user_id, payment_status='completed')
    
    # Get videos and bots
    featured_videos = Video.objects.filter(is_active=True)[:3]
    all_videos = Video.objects.filter(is_active=True)
    featured_bots = TradingBot.objects.filter(is_active=True, is_featured=True)[:3]
    all_bots = TradingBot.objects.filter(is_active=True)
    
    for purchase in purchases:
        course = Course.objects.filter(id=purchase.courseId).first()
        if course:
            purchase.course__title = course.title
    
    context = {
        'user': user,
        'all_courses': Course.objects.filter(is_active=True),
        'purchased_courses': purchased_courses_list,
        'purchased_course_ids': purchased_course_ids,
        'purchases': purchases,
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

# ========== PAYMENT VIEWS ==========

def payments(request, amount):
    user_id = request.session.get('user_id')
    if user_id is not None:
        usdprice = amount
        keprice = int(amount * 130)
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['payment_type'] = 'service'
        return render(request, "payments.html", {"usdprice": usdprice, "keprice": keprice})
    else:
        return redirect("/login")

def coursepayments(request, amount, course_id):
    user_id = request.session.get('user_id')
    if user_id is not None:
        usdprice = amount
        keprice = int(amount * 130)
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['courseId'] = course_id
        request.session['payment_type'] = 'course'
        return render(request, "payment.html", {"usdprice": usdprice, "keprice": keprice})
    else:
        return redirect("/login")

def bot_payments(request, bot_id):
    user_id = request.session.get('user_id')
    if user_id is not None:
        bot = TradingBot.objects.get(id=bot_id, is_active=True)
        usdprice = float(bot.price)
        keprice = int(usdprice * 130)
        request.session['usdprice'] = usdprice
        request.session['keprice'] = keprice
        request.session['botId'] = bot_id
        request.session['payment_type'] = 'bot'
        return render(request, "bot_payment.html", {"bot": bot, "usdprice": usdprice, "keprice": keprice})
    else:
        return redirect("/login")

# Simulated MPESA Checkout
def mpesa_checkout(request):
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
            if usdprice == 40:
                service = "SignalsPlan"
            elif usdprice == 150:
                service = "VirtualMentorshipPlan"
            elif usdprice == 250:
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
        else:  # bot
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
            
            # Grant access for courses/bots
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

# Simulated Card Payment
def CardPayments(request):
    user_id = request.session.get('user_id')
    if user_id is not None:
        email = SiteUsers.objects.get(id=user_id).email
        usdprice = request.session.get('usdprice')
        payment_type = request.session.get('payment_type')
        
        if payment_type == 'service':
            if usdprice == 40:
                service = "SignalsPlan"
            elif usdprice == 150:
                service = "VirtualMentorshipPlan"
            elif usdprice == 250:
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
        else:  # bot
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

# Simulated Course MPESA Checkout (kept for compatibility)
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

# Payment Status API Endpoint
@csrf_exempt
def check_payment_status(request):
    payment_id = request.GET.get('payment_id')
    payment_type = request.GET.get('payment_type')
    
    if payment_type == 'service':
        try:
            payment = ServicePayments.objects.get(id=payment_id)
            return JsonResponse({
                'status': payment.payment_status,
                'payment_id': payment.id
            })
        except ServicePayments.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    elif payment_type == 'course':
        try:
            payment = CoursePayments.objects.get(id=payment_id)
            return JsonResponse({
                'status': payment.payment_status,
                'payment_id': payment.id
            })
        except CoursePayments.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)
    else:
        try:
            payment = BotPayments.objects.get(id=payment_id)
            return JsonResponse({
                'status': payment.payment_status,
                'payment_id': payment.id
            })
        except BotPayments.DoesNotExist:
            return JsonResponse({'status': 'not_found'}, status=404)

# API Endpoints
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