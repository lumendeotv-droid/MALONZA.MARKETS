from django.urls import path, register_converter
from . import views
from .converter import FloatConverter
from django.conf import settings
from django.conf.urls.static import static

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
    
    # Service Payments
    path('payments/<float:amount>', views.payments, name='payments'),
    path('mpesa_checkout', views.mpesa_checkout, name='mpesa_checkout'),
    path('card_checkout', views.CardPayments, name="card_checkout"),
    
    # Course Payments
    path('coursepayments/<float:amount>/<int:course_id>/', views.coursepayments, name='coursepayments'),
    path('course_mpesa_checkout', views.course_mpesa_checkout, name='course_mpesa_checkout'),
    path('course_card_checkout', views.course_cardPayments, name="course_card_checkout"),
    
    # Bot Payments
    path('bot-payments/<int:bot_id>/', views.bot_payments, name='bot_payments'),
    path('bot_mpesa_checkout', views.bot_mpesa_checkout, name='bot_mpesa_checkout'),
    path('bot_card_checkout', views.bot_card_payments, name='bot_card_checkout'),
    
    # Payment Status API
    path('api/payment-status/', views.check_payment_status, name='payment_status'),
    
    # API Endpoints
    path('api/subscribe', views.subscribe_newsletter, name='subscribe'),
    path('api/contact', views.submit_contact, name='contact_api'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)