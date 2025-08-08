from django.db import models
from django.utils import timezone


class PriceData(models.Model):
    """مدل ذخیره داده‌های قیمت بهینه شده"""
    
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
    
    # اطلاعات اصلی
    commodity_name = models.CharField(max_length=100, choices=COMMODITY_CHOICES, verbose_name="نام کالا", db_index=True)
    symbol = models.CharField(max_length=50, verbose_name="نماد", blank=True, db_index=True)
    
    # قیمت‌ها - استفاده از DecimalField برای دقت بیشتر
    final_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت نهایی")
    avg_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت میانگین")
    max_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="بیشترین قیمت")
    min_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="کمترین قیمت")
    base_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت پایه")
    
    # حجم‌ها
    volume = models.PositiveIntegerField(default=0, verbose_name="حجم معاملات")
    transaction_count = models.PositiveIntegerField(default=0, verbose_name="تعداد معاملات")
    
    # تاریخ - استفاده از DateField
    price_date = models.DateField(db_index=True, verbose_name="تاریخ")
    
    # منبع داده
    source = models.CharField(max_length=50, default='scroll_time', verbose_name="منبع", db_index=True)
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    
    class Meta:
        verbose_name = "داده قیمت"
        verbose_name_plural = "داده‌های قیمت"
        # ایندکس ترکیبی برای جستجوی سریع
        indexes = [
            models.Index(fields=['commodity_name', 'price_date']),
            models.Index(fields=['symbol', 'price_date']),
            models.Index(fields=['source', 'created_at']),
        ]
        # جلوگیری از تکرار داده‌ها
        unique_together = ['commodity_name', 'symbol', 'price_date', 'source']
        
    def __str__(self):
        return f"{self.commodity_name} - {self.price_date}"


class Category(models.Model):
    """دسته‌بندی‌های کالا"""
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    value = models.IntegerField(verbose_name="مقدار")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="والد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    
    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['value']),
        ]
        
    def __str__(self):
        return self.name


class DataImportLog(models.Model):
    """لاگ واردات داده‌ها"""
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]
    
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا")
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    total_records = models.PositiveIntegerField(default=0, verbose_name="تعداد کل رکوردها")
    imported_records = models.PositiveIntegerField(default=0, verbose_name="تعداد رکوردهای وارد شده")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    created_by = models.CharField(max_length=150, blank=True, verbose_name="ایجاد شده توسط")
    
    class Meta:
        verbose_name = "لاگ واردات"
        verbose_name_plural = "لاگ‌های واردات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['commodity_name', 'start_date']),
        ]
        
    def __str__(self):
        return f"{self.commodity_name} - {self.status}"
