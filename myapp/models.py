from django.db import models
from django.utils.timezone import now
import re

class SiteUsers(models.Model):
    email = models.EmailField(unique=True)
    password = models.TextField()
    username = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.email} : {self.username}'


# ========== HOMEPAGE DYNAMIC SECTIONS ==========

class HeroSection(models.Model):
    title_1 = models.CharField(max_length=200, default="Systematic Trading Approach")
    subtitle_1 = models.CharField(max_length=200, default="QUANTITATIVE · SYSTEMATIC · RULE-BASED")
    description_1 = models.TextField(default="Data analysis · Statistical modeling · Predefined execution rules")
    button1_text_1 = models.CharField(max_length=50, default="Get Free Signals")
    button2_text_1 = models.CharField(max_length=50, default="Learn More")
    image_1 = models.ImageField(upload_to='hero/', blank=True, null=True)
    
    title_2 = models.CharField(max_length=200, default="Disciplined Execution")
    subtitle_2 = models.CharField(max_length=200, default="RISK MANAGEMENT · STRUCTURED EXPOSURE")
    description_2 = models.TextField(default="Controlled position sizing · Continuous evaluation · Repeatable processes")
    button1_text_2 = models.CharField(max_length=50, default="Join Free Telegram")
    button2_text_2 = models.CharField(max_length=50, default="Our Strategy")
    image_2 = models.ImageField(upload_to='hero/', blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Hero Section"
    
    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"


class AboutSection(models.Model):
    badge_text = models.CharField(max_length=100, default="ABOUT OUR TRADING HUB")
    title = models.CharField(max_length=200, default="Master the Markets with 5+ Years of Proven Expertise")
    description = models.TextField(default="At Malonza Markets®, we combine cutting-edge strategies with psychological mastery to create disciplined traders.")
    experience_years = models.IntegerField(default=5)
    phone_number = models.CharField(max_length=20, default="+254 703 987 878")
    phone_label = models.CharField(max_length=100, default="Ready to start?")
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    telegram_link = models.URLField(default="https://t.me/malonzamarkets")
    whatsapp_link = models.URLField(default="https://wa.me/254703987878")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "About Section"
    
    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Section"


class Fact(models.Model):
    ICON_CHOICES = [
        ('fa-users', 'Users Icon'),
        ('fa-check', 'Check Icon'),
        ('fa-trophy', 'Trophy Icon'),
    ]
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-users')
    title = models.CharField(max_length=100)
    count = models.IntegerField(default=0)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Fact"
        verbose_name_plural = "Facts"
    
    def __str__(self):
        return self.title


class Feature(models.Model):
    ICON_CHOICES = [
        ('fas fa-user-tie', 'Expertise'),
        ('fas fa-users', 'Community'),
        ('fas fa-tree', 'Growth'),
        ('fa fa-phone-alt', 'Support'),
    ]
    icon = models.CharField(max_length=50, choices=ICON_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Feature"
        verbose_name_plural = "Features"
    
    def __str__(self):
        return self.title


class Service(models.Model):
    ICON_CHOICES = [
        ('fas fa-newspaper', 'Newspaper'),
        ('fas fa-broadcast-tower', 'Broadcast'),
        ('fas fa-crown', 'Crown'),
        ('fas fa-chalkboard-teacher', 'Teacher'),
        ('fas fa-copy', 'Copy'),
        ('fas fa-chart-line', 'Chart'),
    ]
    icon = models.CharField(max_length=50, choices=ICON_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price_text = models.CharField(max_length=100, default="FREE")
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Service"
        verbose_name_plural = "Services"
    
    def __str__(self):
        return self.title


class PricingPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price_usd = models.FloatField()
    price_kes = models.FloatField(default=0)
    period = models.CharField(max_length=50, default="/month")
    features = models.TextField(help_text="Enter each feature on a new line")
    is_popular = models.BooleanField(default=False)
    button_text = models.CharField(max_length=50, default="Get Started")
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Pricing Plan"
        verbose_name_plural = "Pricing Plans"
    
    def get_features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]
    
    def __str__(self):
        return self.name


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default="Student")
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return self.name


class Broker(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brokers/')
    qr_code = models.ImageField(upload_to='brokers/qr/', blank=True, null=True)
    link = models.URLField()
    button_text = models.CharField(max_length=50, default="Start Trading")
    description = models.CharField(max_length=200, blank=True, null=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Broker"
        verbose_name_plural = "Brokers"
    
    def __str__(self):
        return self.name


class SocialLink(models.Model):
    platform = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"
    
    def __str__(self):
        return self.platform


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    package = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    reply_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Malonza Markets")
    site_logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True)
    footer_text = models.TextField(default="Welcome to Malonza Markets® where Africa's top traders gather...")
    copyright_text = models.CharField(max_length=200, default="© Malonza Markets®. All Rights Reserved.")
    disclaimer_text = models.TextField(default="Disclaimer: Malonza is not a certified financial advisor...")
    contact_email = models.EmailField(default="malonzanicholas@gmail.com")
    contact_phone = models.CharField(max_length=20, default="+254703987878")
    contact_address = models.CharField(max_length=200, default="Nairobi, Kenya")
    support_response_time = models.CharField(max_length=100, default="Reply within 24 hours")
    support_phone_available = models.CharField(max_length=100, default="24 hrs telephone support")
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Site Settings"
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"


# ========== VIDEOS LIBRARY (FREE CONTENT) ==========
class Video(models.Model):
    VIDEO_TYPE_CHOICES = [
        ('youtube', 'YouTube Link'),
        ('upload', 'Upload Video File'),
    ]
    
    title = models.CharField(max_length=200)
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPE_CHOICES, default='youtube', help_text="Choose video source")
    video_url = models.URLField(blank=True, null=True, help_text="Paste full YouTube URL")
    video_file = models.FileField(upload_to='videos/', blank=True, null=True, help_text="Upload MP4, WebM, or OGG video file")
    description = models.TextField(blank=True, null=True)
    use_custom_thumbnail = models.BooleanField(default=False)
    custom_thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Video"
        verbose_name_plural = "Videos"
    
    def get_youtube_id(self):
        if not self.video_url:
            return None
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
            r'(?:youtube\.com\/shorts\/)([\w-]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                return match.group(1)
        return None
    
    def get_thumbnail_url(self):
        if self.use_custom_thumbnail and self.custom_thumbnail:
            return self.custom_thumbnail.url
        video_id = self.get_youtube_id()
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        return None
    
    def get_video_url(self):
        if self.video_type == 'youtube' and self.video_url:
            video_id = self.get_youtube_id()
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
            return self.video_url
        elif self.video_type == 'upload' and self.video_file:
            return self.video_file.url
        return None
    
    def get_watch_url(self):
        if self.video_type == 'youtube':
            return self.video_url
        return self.video_file.url if self.video_file else None
    
    def __str__(self):
        return self.title


# ========== COURSE VIDEOS (COURSE-SPECIFIC CONTENT) ==========
class CourseVideo(models.Model):
    VIDEO_TYPE_CHOICES = [
        ('youtube', 'YouTube Link'),
        ('upload', 'Upload Video File'),
    ]
    
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='course_videos')
    title = models.CharField(max_length=200)
    video_type = models.CharField(max_length=10, choices=VIDEO_TYPE_CHOICES, default='youtube')
    video_url = models.URLField(blank=True, null=True, help_text="YouTube URL for this lesson")
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True, help_text="Upload MP4 video file for this lesson")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Course Video"
        verbose_name_plural = "Course Videos"
    
    def get_youtube_id(self):
        if not self.video_url:
            return None
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([\w-]+)',
            r'(?:youtu\.be\/)([\w-]+)',
            r'(?:youtube\.com\/embed\/)([\w-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.video_url)
            if match:
                return match.group(1)
        return None
    
    def get_embed_url(self):
        if self.video_type == 'youtube' and self.video_url:
            video_id = self.get_youtube_id()
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
            return self.video_url
        elif self.video_type == 'upload' and self.video_file:
            return self.video_file.url
        return None
    
    def get_watch_url(self):
        if self.video_type == 'youtube':
            return self.video_url
        return self.video_file.url if self.video_file else None
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


# ========== COURSES SECTION ==========
class Course(models.Model):
    title = models.CharField(max_length=255)
    priceusd = models.FloatField(default=0.0)
    pricekes = models.FloatField(default=0.0)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='courses/')
    pdf = models.FileField(upload_to='pdfs/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
    
    def __str__(self):
        return self.title


class UserCourseAccess(models.Model):
    user = models.ForeignKey(SiteUsers, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class ServicePayments(models.Model):
    email = models.EmailField()
    service = models.CharField(max_length=100)
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='initialized')
    payment_method = models.CharField(max_length=20, default='mpesa')
    
    def __str__(self):
        return f"{self.email} - {self.service} - {self.payment_status}"


class CoursePayments(models.Model):
    email = models.EmailField()
    courseId = models.IntegerField()
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='initialized')
    payment_method = models.CharField(max_length=20, default='mpesa')
    
    def __str__(self):
        return f"{self.email} - Course {self.courseId} - {self.payment_status}"


# ========== TRADING BOTS SECTION ==========
class TradingBot(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='bots/')
    pdf = models.FileField(upload_to='bot_pdfs/', blank=True, null=True, help_text="Upload PDF file for the bot")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Trading Bot"
        verbose_name_plural = "Trading Bots"
    
    def __str__(self):
        return self.name


# ========== BOT PAYMENTS AND ACCESS ==========
class BotPayments(models.Model):
    email = models.EmailField()
    botId = models.IntegerField()
    userId = models.IntegerField()
    amountkes = models.FloatField(default=0.0)
    amountusd = models.FloatField(default=0.0)
    mpesa_number = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='pending')
    payment_method = models.CharField(max_length=20, default='mpesa')
    
    def __str__(self):
        return f"{self.email} - Bot {self.botId} - {self.payment_status}"


class UserBotAccess(models.Model):
    user = models.ForeignKey(SiteUsers, on_delete=models.CASCADE)
    bot = models.ForeignKey(TradingBot, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'bot']
    
    def __str__(self):
        return f"{self.user.username} - {self.bot.name}"


# ========== BLOG SECTION ==========
class Blog(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True, null=True, help_text="Short description shown on blog cards")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def __str__(self):
        return self.title


# ========== PERFORMANCE STATS SECTION ==========
class PerformanceStats(models.Model):
    overall_win_rate = models.FloatField(default=78.5, help_text="Overall win rate percentage")
    weekly_win_rate = models.FloatField(default=82.3, help_text="Weekly win rate percentage")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Performance Stat"
        verbose_name_plural = "Performance Stats"
    
    def __str__(self):
        return f"Performance Stats - Overall: {self.overall_win_rate}% | Weekly: {self.weekly_win_rate}%"