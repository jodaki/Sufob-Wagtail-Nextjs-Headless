from django.db import models
from django.utils import timezone


class MainCategory(models.Model):
    """گروه‌های اصلی (MainCat) برای Scroll Time API"""
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


class Category(models.Model):
    """گروه‌ها (Cat) برای Scroll Time API"""
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, verbose_name="گروه اصلی")
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


class SubCategory(models.Model):
    """زیرگروه‌ها (SubCat) برای Scroll Time API"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="گروه")
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


class ScrollTimeRequest(models.Model):
    """درخواست‌های Scroll Time"""
    DUPLICATE_HANDLING_CHOICES = [
        ('skip', 'رد کردن رکوردهای تکراری'),
        ('replace', 'جایگزینی رکوردهای تکراری'),
        ('update', 'بروزرسانی رکوردهای موجود'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('pending', 'در انتظار'),
        ('processing', 'در حال پردازش'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]
    
    # دسته‌بندی‌ها
    main_category = models.ForeignKey(
        MainCategory, 
        on_delete=models.CASCADE, 
        verbose_name="دسته اصلی"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        verbose_name="دسته"
    )
    subcategory = models.ForeignKey(
        SubCategory, 
        on_delete=models.CASCADE, 
        verbose_name="زیردسته"
    )
    
    # تاریخ‌ها
    start_date_shamsi = models.CharField(max_length=10, verbose_name="تاریخ شروع (شمسی)")
    end_date_shamsi = models.CharField(max_length=10, verbose_name="تاریخ پایان (شمسی)")
    start_date_gregorian = models.DateField(null=True, blank=True, verbose_name="تاریخ شروع (میلادی)")
    end_date_gregorian = models.DateField(null=True, blank=True, verbose_name="تاریخ پایان (میلادی)")
    
    # تنظیمات پردازش
    duplicate_handling = models.CharField(
        max_length=20, 
        choices=DUPLICATE_HANDLING_CHOICES, 
        default='skip',
        verbose_name="نحوه مواجهه با داده‌های تکراری"
    )
    auto_save = models.BooleanField(default=False, verbose_name="ذخیره خودکار در پایگاه داده")
    
    # وضعیت و نتایج
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="وضعیت")
    total_records = models.PositiveIntegerField(default=0, verbose_name="تعداد کل رکوردها")
    processed_records = models.PositiveIntegerField(default=0, verbose_name="تعداد رکوردهای پردازش شده")
    response_data = models.JSONField(null=True, blank=True, verbose_name="داده‌های پاسخ")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان بروزرسانی")
    created_by = models.CharField(max_length=150, blank=True, verbose_name="ایجاد شده توسط")
    
    class Meta:
        verbose_name = "درخواست Scroll Time"
        verbose_name_plural = "درخواست‌های Scroll Time"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['main_category', 'category']),
        ]
        
    def __str__(self):
        return f"درخواست {self.id} - {self.status}"
    
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
