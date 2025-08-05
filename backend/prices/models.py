from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail_headless_preview.models import HeadlessPreviewMixin
from django.utils import timezone


class PriceIndexPage(HeadlessPreviewMixin, Page):
    """صفحه index برای قیمت‌ها - Headless CMS"""
    intro = RichTextField(blank=True, help_text="مقدمه صفحه قیمت‌ها")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    # API fields for Next.js frontend
    api_fields = [
        APIField('intro'),
    ]
    
    # تعیین کنید که چه نوع صفحه‌هایی می‌توانند فرزند این صفحه باشند
    subpage_types = ['prices.PricePage']
    
    class Meta:
        verbose_name = "صفحه قیمت‌ها"
        verbose_name_plural = "صفحات قیمت‌ها"


class PricePage(HeadlessPreviewMixin, Page):
    """صفحه نمایش چارت قیمت برای یک کالا - Headless CMS"""
    COMMODITY_CHOICES = [
        ('کنسانتره آهن', 'کنسانتره آهن'),
        ('سنگ آهن', 'سنگ آهن'),
        ('کاتد مس', 'کاتد مس'),
        ('شمش آلومینیوم', 'شمش آلومینیوم'),
        ('کک متالورژی', 'کک متالورژی'),
    ]
    
    commodity_name = models.CharField(
        max_length=100, 
        choices=COMMODITY_CHOICES,
        help_text="نام کالا را انتخاب کنید"
    )
    chart_description = RichTextField(blank=True, help_text="توضیحات چارت")
    show_statistics = models.BooleanField(default=True, help_text="نمایش آمار")
    chart_days = models.IntegerField(default=30, help_text="تعداد روزهای نمایش در چارت")
    
    content_panels = Page.content_panels + [
        FieldPanel('commodity_name'),
        FieldPanel('chart_description'),
        FieldPanel('show_statistics'),
        FieldPanel('chart_days'),
    ]
    
    # API fields for Next.js frontend
    api_fields = [
        APIField('commodity_name'),
        APIField('chart_description'),
        APIField('show_statistics'),
        APIField('chart_days'),
    ]
    
    # تعیین کنید که این صفحه فقط می‌تواند فرزند PriceIndexPage باشد
    parent_page_types = ['prices.PriceIndexPage']
    subpage_types = []  # این صفحه نمی‌تواند فرزند داشته باشد
    
    class Meta:
        verbose_name = "صفحه قیمت کالا"
        verbose_name_plural = "صفحات قیمت کالا"


# مدل‌های جدید برای ذخیره داده‌های قیمت
class PriceData(models.Model):
    """مدل اصلی برای ذخیره داده‌های قیمت کالاها"""
    COMMODITY_CHOICES = [
        ('کنسانتره آهن', 'کنسانتره آهن'),
        ('سنگ آهن', 'سنگ آهن'),
        ('کاتد مس', 'کاتد مس'),
        ('شمش آلومینیوم', 'شمش آلومینیوم'),
        ('کک متالورژی', 'کک متالورژی'),
        ('طلا', 'طلا'),
        ('نقره', 'نقره'),
        ('مس', 'مس'),
        ('آلومینیوم', 'آلومینیوم'),
        ('روی', 'روی'),
    ]
    
    commodity_name = models.CharField(max_length=100, choices=COMMODITY_CHOICES, verbose_name="نام کالا")
    symbol = models.CharField(max_length=50, blank=True, verbose_name="نماد")
    price_date = models.DateField(verbose_name="تاریخ قیمت")
    final_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت نهایی")
    avg_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت متوسط")
    lowest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="کمترین قیمت")
    highest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="بیشترین قیمت")
    volume = models.BigIntegerField(null=True, blank=True, verbose_name="حجم معاملات")
    value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="ارزش معاملات")
    unit = models.CharField(max_length=20, blank=True, verbose_name="واحد")
    
    # متاداده
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    source = models.CharField(max_length=100, default='manual', verbose_name="منبع داده")
    
    class Meta:
        verbose_name = "داده قیمت"
        verbose_name_plural = "داده‌های قیمت"
        unique_together = [['commodity_name', 'price_date']]  # جلوگیری از تکرار
        ordering = ['-price_date', 'commodity_name']
        indexes = [
            models.Index(fields=['commodity_name', 'price_date']),
            models.Index(fields=['price_date']),
        ]
    
    def __str__(self):
        return f"{self.commodity_name} - {self.price_date} - {self.final_price}"
    
    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('commodity_name'),
            FieldPanel('symbol'),
            FieldPanel('price_date'),
        ], heading='اطلاعات کلی'),
        MultiFieldPanel([
            FieldPanel('final_price'),
            FieldPanel('avg_price'),
            FieldPanel('lowest_price'),
            FieldPanel('highest_price'),
        ], heading='قیمت‌ها'),
        MultiFieldPanel([
            FieldPanel('volume'),
            FieldPanel('value'),
            FieldPanel('unit'),
        ], heading='حجم و ارزش'),
        MultiFieldPanel([
            FieldPanel('source'),
        ], heading='اطلاعات تکمیلی'),
    ]


class DataImportLog(models.Model):
    """لاگ عملیات‌های وارد کردن داده"""
    STATUS_CHOICES = [
        ('success', 'موفق'),
        ('error', 'خطا'),
        ('partial', 'جزئی'),
    ]
    
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    total_records = models.IntegerField(default=0, verbose_name="تعداد کل رکوردها")
    imported_records = models.IntegerField(default=0, verbose_name="رکوردهای وارد شده")
    updated_records = models.IntegerField(default=0, verbose_name="رکوردهای بروزرسانی شده")
    duplicate_records = models.IntegerField(default=0, verbose_name="رکوردهای تکراری")
    error_records = models.IntegerField(default=0, verbose_name="رکوردهای خطا")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="وضعیت")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="ایجاد شده توسط")
    
    class Meta:
        verbose_name = "لاگ وارد کردن داده"
        verbose_name_plural = "لاگ‌های وارد کردن داده"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.commodity_name} - {self.start_date} تا {self.end_date} - {self.status}"
    
    # Wagtail admin panels
    panels = [
        MultiFieldPanel([
            FieldPanel('commodity_name'),
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ], heading='اطلاعات کلی'),
        MultiFieldPanel([
            FieldPanel('total_records'),
            FieldPanel('imported_records'),
            FieldPanel('updated_records'),
            FieldPanel('duplicate_records'),
            FieldPanel('error_records'),
        ], heading='آمار رکوردها'),
        MultiFieldPanel([
            FieldPanel('status'),
            FieldPanel('error_message'),
            FieldPanel('created_by'),
        ], heading='اطلاعات وضعیت'),
    ]


# مدل‌های جدید برای Scroll Time
class MainCategory(models.Model):
    """گروه‌های اصلی (MainCat)"""
    value = models.IntegerField(unique=True, verbose_name="مقدار (API Value)")
    name = models.CharField(max_length=100, verbose_name="نام گروه اصلی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "گروه اصلی"
        verbose_name_plural = "گروه‌های اصلی"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['value']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.value})"
    
    panels = [
        FieldPanel('name'),
        FieldPanel('value'),
        FieldPanel('is_active'),
        FieldPanel('order'),
    ]


class Category(models.Model):
    """گروه‌ها (Cat)"""
    main_category = models.ForeignKey(
        MainCategory, 
        on_delete=models.CASCADE, 
        related_name='categories',
        verbose_name="گروه اصلی"
    )
    value = models.IntegerField(verbose_name="مقدار (API Value)")
    name = models.CharField(max_length=100, verbose_name="نام گروه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "گروه"
        verbose_name_plural = "گروه‌ها"
        ordering = ['main_category', 'order', 'name']
        unique_together = [['main_category', 'value']]
        indexes = [
            models.Index(fields=['main_category', 'value']),
        ]
    
    def __str__(self):
        return f"{self.main_category.name} -> {self.name} ({self.value})"
    
    panels = [
        FieldPanel('main_category'),
        FieldPanel('name'),
        FieldPanel('value'),
        FieldPanel('is_active'),
        FieldPanel('order'),
    ]


class SubCategory(models.Model):
    """زیرگروه‌ها (SubCat)"""
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='subcategories',
        verbose_name="گروه"
    )
    value = models.IntegerField(verbose_name="مقدار (API Value)")
    name = models.CharField(max_length=100, verbose_name="نام زیرگروه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.IntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    
    class Meta:
        verbose_name = "زیرگروه"
        verbose_name_plural = "زیرگروه‌ها"
        ordering = ['category', 'order', 'name']
        unique_together = [['category', 'value']]
        indexes = [
            models.Index(fields=['category', 'value']),
        ]
    
    def __str__(self):
        return f"{self.category.main_category.name} -> {self.category.name} -> {self.name} ({self.value})"
    
    panels = [
        FieldPanel('category'),
        FieldPanel('name'),
        FieldPanel('value'),
        FieldPanel('is_active'),
        FieldPanel('order'),
    ]


class ScrollTimeRequest(models.Model):
    """درخواست‌های Scroll Time برای دریافت داده از سرور بورس"""
    DUPLICATE_HANDLING_CHOICES = [
        ('skip', 'رد کردن رکوردهای تکراری'),
        ('replace', 'جایگزینی رکوردهای تکراری'),
        ('update', 'بروزرسانی رکوردهای موجود'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('preview', 'پیش‌نمایش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]
    
    # انتخاب دسته‌بندی
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, verbose_name="گروه اصلی")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="گروه")
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, verbose_name="زیرگروه")
    
    # بازه زمانی (تقویم شمسی)
    start_date_shamsi = models.CharField(max_length=10, verbose_name="تاریخ شروع (شمسی)")
    end_date_shamsi = models.CharField(max_length=10, verbose_name="تاریخ پایان (شمسی)")
    
    # تنظیمات پردازش
    duplicate_handling = models.CharField(
        max_length=20, 
        choices=DUPLICATE_HANDLING_CHOICES, 
        default='skip',
        verbose_name="نحوه مواجهه با داده‌های تکراری"
    )
    auto_save = models.BooleanField(default=False, verbose_name="ذخیره خودکار در پایگاه داده")
    
    # وضعیت و نتایج
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت درخواست")
    response_data = models.JSONField(null=True, blank=True, verbose_name="داده‌های پاسخ")
    total_records = models.IntegerField(default=0, verbose_name="تعداد کل رکوردها")
    processed_records = models.IntegerField(default=0, verbose_name="رکوردهای پردازش شده")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    
    # متاداده
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="ایجاد شده توسط")
    
    class Meta:
        verbose_name = "درخواست Scroll Time"
        verbose_name_plural = "درخواست‌های Scroll Time"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.main_category.name} -> {self.category.name} -> {self.subcategory.name} ({self.start_date_shamsi} تا {self.end_date_shamsi})"
    
    def get_payload(self):
        """ایجاد payload برای ارسال به سرور بورس"""
        return {
            'Language': 8,
            'fari': False,
            'GregorianFromDate': self.start_date_shamsi,
            'GregorianToDate': self.end_date_shamsi,
            'MainCat': self.main_category.value if self.main_category else 0,
            'Cat': self.category.value if self.category else 0,
            'SubCat': self.subcategory.value if self.subcategory else 0,
            'Producer': 0
        }
    
    panels = [
        MultiFieldPanel([
            FieldPanel('main_category'),
            FieldPanel('category'),
            FieldPanel('subcategory'),
        ], heading='انتخاب دسته‌بندی'),
        MultiFieldPanel([
            FieldPanel('start_date_shamsi'),
            FieldPanel('end_date_shamsi'),
        ], heading='بازه زمانی'),
        MultiFieldPanel([
            FieldPanel('duplicate_handling'),
            FieldPanel('auto_save'),
        ], heading='تنظیمات پردازش'),
        MultiFieldPanel([
            FieldPanel('status'),
            FieldPanel('total_records'),
            FieldPanel('processed_records'),
            FieldPanel('error_message'),
        ], heading='اطلاعات وضعیت'),
    ]
