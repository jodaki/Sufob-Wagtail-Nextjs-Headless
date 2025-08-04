from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
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
