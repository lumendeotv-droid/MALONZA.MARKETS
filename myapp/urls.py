from django.urls import path, register_converter
from . import views
from django.conf import settings
from django.conf.urls.static import static

# Custom converter for float amounts
class FloatConverter:
    regex = r'[\d]+\.?[\d]*'
    
    def to_python(self, value):
        return float(value)
    
    def to_url(self, value):
        return str(value)

register_converter(FloatConverter, 'float')

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('update_profile', views.update_profile, name='update_profile'),
    
    # Authentication
    path('register', views.register, name='register'),
    path('login', views.login_page, name='login'),
    path('forgot', views.forgot, name='forgot'),
    path('create_account', views.create_account, name='create_account'),
    path('auth_login', views.auth_login, name='auth_login'),
    path('logout', views.logout, name='logout'),
    
    # Service Payments ($50, $500, $750)
    path('payments/<float:amount>', views.payments, name='payments'),
    
    # Course Payments
    path('coursepayments/<float:amount>/<int:course_id>/', views.coursepayments, name='coursepayments'),
    
    # Bot Payments
    path('bot-payments/<int:bot_id>/', views.bot_payments, name='bot_payments'),
    
    # ========== PAYSTACK ROUTES ==========
    path('paystack/initialize/', views.paystack_initialize, name='paystack_initialize'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
    path('paystack/webhook/', views.paystack_webhook, name='paystack_webhook'),
    
    # Payment Status API
    path('api/payment-status/', views.check_payment_status, name='payment_status'),
    path('api/get_user_email/', views.get_user_email, name='get_user_email'),
    
    # Legacy routes (kept for backward compatibility)
    path('mpesa_checkout', views.mpesa_checkout, name='mpesa_checkout'),
    path('card_checkout', views.CardPayments, name="card_checkout"),
    path('course_mpesa_checkout', views.course_mpesa_checkout, name='course_mpesa_checkout'),
    path('course_card_checkout', views.course_cardPayments, name="course_card_checkout"),
    path('bot_mpesa_checkout', views.bot_mpesa_checkout, name='bot_mpesa_checkout'),
    path('bot_card_checkout', views.bot_card_payments, name='bot_card_checkout'),
    
    # API Endpoints
    path('api/subscribe', views.subscribe_newsletter, name='subscribe'),
    path('api/contact', views.submit_contact, name='contact_api'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)