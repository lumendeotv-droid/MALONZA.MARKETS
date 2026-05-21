from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.admin import AdminSite
from .models import *

# ========== CUSTOM ADMIN SITE WITH MALONZA THEME ==========
class MalonzaAdminSite(AdminSite):
    site_header = "Malonza Markets Admin Panel"
    site_title = "Malonza Markets Admin"
    index_title = "Dashboard - Manage Your Trading Platform"
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        
        ordered_models = [
            'HeroSection', 'AboutSection', 'SiteSettings', 'PerformanceStats',
            'Fact', 'Feature', 'Service', 'PricingPlan',
            'Video', 'TradingBot', 'Blog',
            'Course', 'CourseVideo', 'Testimonial', 'Broker', 'SocialLink',
            'SiteUsers', 'ContactMessage', 'NewsletterSubscription',
            'ServicePayments', 'CoursePayments', 'UserCourseAccess', 'BotPayments', 'UserBotAccess'
        ]
        
        for app in app_list:
            if app['app_label'] == 'myapp':
                app['models'].sort(key=lambda x: ordered_models.index(x['object_name']) if x['object_name'] in ordered_models else 999)
        
        return app_list

admin_site = MalonzaAdminSite(name='malonza_admin')

class MalonzaModelAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('admin/css/malonza-admin.css',)
        }

# ========== SITE CONTENT SECTION ==========
class HeroSectionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('📸 Slide 1', {
            'fields': ('title_1', 'subtitle_1', 'description_1', 'button1_text_1', 'button2_text_1', 'image_1'),
        }),
        ('📸 Slide 2', {
            'fields': ('title_2', 'subtitle_2', 'description_2', 'button1_text_2', 'button2_text_2', 'image_2'),
        }),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

class AboutSectionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('🏢 General Settings', {'fields': ('site_name', 'site_logo', 'favicon')}),
        ('📝 Footer & Legal', {'fields': ('footer_text', 'copyright_text', 'disclaimer_text')}),
        ('📞 Contact Information', {'fields': ('contact_email', 'contact_phone', 'contact_address', 'support_response_time', 'support_phone_available')}),
    )
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

class PerformanceStatsAdmin(admin.ModelAdmin):
    list_display = ['overall_win_rate', 'weekly_win_rate', 'updated_at']
    
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

# ========== CONTENT SECTIONS ==========
class FactAdmin(admin.ModelAdmin):
    list_display = ['icon_display', 'title', 'count', 'order']
    list_editable = ['order', 'count']
    
    def icon_display(self, obj):
        icons = {'fa-users': '👥', 'fa-check': '✓', 'fa-trophy': '🏆'}
        return icons.get(obj.icon, '📊')
    icon_display.short_description = 'Icon'

class FeatureAdmin(admin.ModelAdmin):
    list_display = ['icon_display', 'title', 'order']
    list_editable = ['order']
    
    def icon_display(self, obj):
        icons = {'fas fa-user-tie': '👔', 'fas fa-users': '👥', 'fas fa-tree': '🌳', 'fa fa-phone-alt': '📞'}
        return icons.get(obj.icon, '⭐')
    icon_display.short_description = 'Icon'

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title_display', 'price_text', 'is_featured', 'order']
    list_editable = ['order', 'is_featured', 'price_text']
    
    def title_display(self, obj):
        return f"📦 {obj.title}"
    title_display.short_description = 'Service'

class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ['name_display', 'price_usd', 'is_popular', 'order']
    list_editable = ['order', 'is_popular']
    
    def name_display(self, obj):
        star = "⭐ " if obj.is_popular else ""
        return f"{star}{obj.name}"
    name_display.short_description = 'Plan'

# ========== VIDEOS SECTION WITH FILE UPLOAD ==========
class VideoAdmin(admin.ModelAdmin):
    list_display = ['thumbnail_preview', 'title', 'video_type', 'is_active', 'order', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'video_type', 'created_at']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Video Information', {
            'fields': ('title', 'video_type', 'description', 'is_active', 'order')
        }),
        ('Video Source', {
            'fields': ('video_url', 'video_file'),
            'description': 'For YouTube: Enter URL. For Upload: Select a video file (MP4, WebM, OGG)'
        }),
        ('Thumbnail Settings', {
            'fields': ('use_custom_thumbnail', 'custom_thumbnail'),
            'description': 'Upload a custom thumbnail or use YouTube default'
        }),
        ('Preview', {
            'fields': ('video_preview', 'thumbnail_display'),
            'classes': ('wide',)
        }),
    )
    readonly_fields = ['video_preview', 'thumbnail_display']
    
    def thumbnail_preview(self, obj):
        if obj.use_custom_thumbnail and obj.custom_thumbnail:
            return format_html('<img src="{}" width="80" height="45" style="object-fit:cover;" />', obj.custom_thumbnail.url)
        elif obj.video_type == 'youtube' and obj.get_thumbnail_url():
            return format_html('<img src="{}" width="80" height="45" style="object-fit:cover;" />', obj.get_thumbnail_url())
        elif obj.video_file:
            return format_html('<video width="80" height="45" style="object-fit:cover;"><source src="{}" type="video/mp4"></video>', obj.video_file.url)
        return "No Preview"
    thumbnail_preview.short_description = 'Thumbnail'
    
    def thumbnail_display(self, obj):
        if obj.use_custom_thumbnail and obj.custom_thumbnail:
            return format_html(
                '<div style="margin-top:10px;"><img src="{}" width="320" height="180" style="object-fit:cover;" /><p style="margin-top:5px; color:#28a745;">✅ Using custom uploaded thumbnail</p></div>',
                obj.custom_thumbnail.url
            )
        elif obj.video_type == 'youtube' and obj.get_thumbnail_url():
            return format_html(
                '<div style="margin-top:10px;"><img src="{}" width="320" height="180" style="object-fit:cover;" /><p style="margin-top:5px; color:#666;">🎬 Using YouTube default thumbnail</p></div>',
                obj.get_thumbnail_url()
            )
        elif obj.video_file:
            return format_html(
                '<div style="margin-top:10px;"><video width="320" height="180" controls style="background:#000;"><source src="{}" type="video/mp4"></video><p style="margin-top:5px; color:#28a745;">✅ Uploaded video file</p></div>',
                obj.video_file.url
            )
        return "No thumbnail available"
    thumbnail_display.short_description = 'Thumbnail Display'
    
    def video_preview(self, obj):
        if obj.video_type == 'youtube' and obj.video_url:
            video_id = obj.get_youtube_id()
            if video_id:
                return format_html(
                    '<div style="margin-top:10px;"><iframe width="320" height="180" src="https://www.youtube.com/embed/{}" frameborder="0" allowfullscreen></iframe></div>'
                    '<p style="margin-top:5px; color:#666;">YouTube Video</p>',
                    video_id
                )
        elif obj.video_type == 'upload' and obj.video_file:
            return format_html(
                '<div style="margin-top:10px;"><video width="320" height="180" controls style="background:#000;"><source src="{}" type="video/mp4"></video><p style="margin-top:5px; color:#28a745;">Uploaded Video File</p></div>',
                obj.video_file.url
            )
        return "No video source provided"
    video_preview.short_description = 'Video Preview'

# ========== COURSE VIDEOS INLINE ==========
class CourseVideoInline(admin.TabularInline):
    model = CourseVideo
    extra = 1
    fields = ['title', 'video_type', 'video_url', 'video_file', 'order', 'preview']
    readonly_fields = ['preview']
    ordering = ['order']
    
    def preview(self, obj):
        if obj.id:
            if obj.video_type == 'youtube' and obj.video_url:
                video_id = obj.get_youtube_id()
                if video_id:
                    return format_html('<iframe width="200" height="113" src="https://www.youtube.com/embed/{}" frameborder="0"></iframe>', video_id)
            elif obj.video_file:
                return format_html('<video width="200" height="113" controls><source src="{}" type="video/mp4"></video>', obj.video_file.url)
        return "Save to see preview"
    preview.short_description = 'Preview'

# ========== TRADING BOTS SECTION ==========
class TradingBotAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'price', 'is_featured', 'is_active', 'order']
    list_editable = ['order', 'is_featured', 'is_active', 'price']
    search_fields = ['name', 'description']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

# ========== BLOG SECTION ==========
class BlogAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'is_active', 'order', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'content', 'excerpt']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

# ========== MARKETING SECTION ==========
class CourseAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'priceusd', 'is_active', 'order']
    list_editable = ['order', 'is_active', 'priceusd']
    inlines = [CourseVideoInline]  # Add inline videos for courses
    search_fields = ['title', 'description']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'is_active', 'order', 'created_at']
    list_editable = ['order', 'is_active']

class BrokerAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo_preview', 'order']
    list_editable = ['order']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:contain;" />', obj.logo.url)
        return "No Logo"
    logo_preview.short_description = 'Logo'

class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['platform', 'icon_preview', 'order']
    list_editable = ['order']
    
    def icon_preview(self, obj):
        return format_html('<i class="{}" style="color:#0088cc; font-size:18px;"></i>', obj.icon_class)
    icon_preview.short_description = 'Icon'

# ========== USERS & MESSAGES SECTION ==========
class SiteUsersAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'created_at', 'status_badge']
    list_filter = ['is_active', 'created_at']
    search_fields = ['username', 'email', 'phone']
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="background:#28a745; color:white; padding:2px 8px;">Active</span>')
        return format_html('<span style="background:#dc3545; color:white; padding:2px 8px;">Inactive</span>')
    status_badge.short_description = 'Status'

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'package', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'phone', 'message']
    
    def status_badge(self, obj):
        colors = {'pending': '#ffc107', 'read': '#17a2b8', 'replied': '#28a745'}
        return format_html('<span style="background:{}; color:white; padding:2px 8px;">{}</span>', 
                          colors.get(obj.status, '#6c757d'), obj.status.upper())
    status_badge.short_description = 'Status'
    
    actions = ['mark_as_read', 'mark_as_replied']
    def mark_as_read(self, request, queryset): queryset.update(status='read')
    def mark_as_replied(self, request, queryset): queryset.update(status='replied')

class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']

# ========== PAYMENTS SECTION ==========
class ServicePaymentsAdmin(admin.ModelAdmin):
    list_display = ['email', 'service', 'amount_display', 'payment_status_badge', 'timestamp']
    list_filter = ['payment_status', 'payment_method', 'timestamp']
    
    def amount_display(self, obj):
        return f"KES {obj.amountkes:,.0f}" if obj.amountkes > 0 else f"${obj.amountusd}"
    amount_display.short_description = 'Amount'
    
    def payment_status_badge(self, obj):
        color = '#28a745' if obj.payment_status == 'completed' else '#ffc107'
        return format_html('<span style="background:{}; color:white; padding:2px 8px;">{}</span>', color, obj.payment_status.upper())
    payment_status_badge.short_description = 'Status'

class CoursePaymentsAdmin(admin.ModelAdmin):
    list_display = ['email', 'course', 'amount_display', 'payment_status_badge', 'timestamp']
    list_filter = ['payment_status', 'payment_method', 'timestamp']
    
    def course(self, obj):
        try:
            return Course.objects.get(id=obj.courseId).title
        except:
            return f"Course #{obj.courseId}"
    course.short_description = 'Course'
    
    def amount_display(self, obj):
        return f"KES {obj.amountkes:,.0f}" if obj.amountkes > 0 else f"${obj.amountusd}"
    amount_display.short_description = 'Amount'
    
    def payment_status_badge(self, obj):
        color = '#28a745' if obj.payment_status == 'completed' else '#ffc107'
        return format_html('<span style="background:{}; color:white; padding:2px 8px;">{}</span>', color, obj.payment_status.upper())
    payment_status_badge.short_description = 'Status'

class UserCourseAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'purchased_at']
    list_filter = ['purchased_at']
    search_fields = ['user__email', 'user__username', 'course__title']

# ========== COURSE VIDEOS ADMIN ==========
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'video_type', 'order', 'created_at']
    list_filter = ['video_type', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    list_editable = ['order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course')

# ========== REGISTER ALL MODELS ==========
admin_site.register(HeroSection, HeroSectionAdmin)
admin_site.register(AboutSection, AboutSectionAdmin)
admin_site.register(SiteSettings, SiteSettingsAdmin)
admin_site.register(PerformanceStats, PerformanceStatsAdmin)
admin_site.register(Fact, FactAdmin)
admin_site.register(Feature, FeatureAdmin)
admin_site.register(Service, ServiceAdmin)
admin_site.register(PricingPlan, PricingPlanAdmin)
admin_site.register(Video, VideoAdmin)
admin_site.register(TradingBot, TradingBotAdmin)
admin_site.register(Blog, BlogAdmin)
admin_site.register(Course, CourseAdmin)
admin_site.register(CourseVideo, CourseVideoAdmin)
admin_site.register(Testimonial, TestimonialAdmin)
admin_site.register(Broker, BrokerAdmin)
admin_site.register(SocialLink, SocialLinkAdmin)
admin_site.register(SiteUsers, SiteUsersAdmin)
admin_site.register(ContactMessage, ContactMessageAdmin)
admin_site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)
admin_site.register(ServicePayments, ServicePaymentsAdmin)
admin_site.register(CoursePayments, CoursePaymentsAdmin)
admin_site.register(UserCourseAccess, UserCourseAccessAdmin)

# Also register with default admin
admin.site.register(HeroSection, HeroSectionAdmin)
admin.site.register(AboutSection, AboutSectionAdmin)
admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(PerformanceStats, PerformanceStatsAdmin)
admin.site.register(Fact, FactAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(PricingPlan, PricingPlanAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(TradingBot, TradingBotAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseVideo, CourseVideoAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
admin.site.register(Broker, BrokerAdmin)
admin.site.register(SocialLink, SocialLinkAdmin)
admin.site.register(SiteUsers, SiteUsersAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)
admin.site.register(ServicePayments, ServicePaymentsAdmin)
admin.site.register(CoursePayments, CoursePaymentsAdmin)
admin.site.register(UserCourseAccess, UserCourseAccessAdmin)