from django.db import models
from django.utils import timezone
from decimal import Decimal
# import jdatetime - disabled for now
        
    def __str__(self):
        return f"{self.symbol} - {self.trade_date_shamsi}"
    
    def save(self, *args, **kwargs):
        """محاسبه نسبت قدرت خریدار به فروشنده هنگام ذخیره"""
        if self.supply_volume and self.supply_volume > 0:
            self.buyer_seller_power_ratio = self.demand_volume / self.supply_volume
        else:
            self.buyer_seller_power_ratio = None
        super().save(*args, **kwargs)


from django.db import models
from django.utils import timezone
import jdatetime


class AllData(models.Model):
    """مدل برای ذخیره تمام داده‌های خام استخراج شده از API سازمان بورس"""
    
    # اطلاعات اصلی نماد
    symbol_code = models.CharField("کد نماد", max_length=20, null=True, blank=True)
    symbol_name = models.CharField("نام نماد", max_length=100, null=True, blank=True)
    company_name = models.CharField("نام شرکت", max_length=200, null=True, blank=True)
    
    # اطلاعات قیمت
    last_price = models.DecimalField("آخرین قیمت", max_digits=15, decimal_places=2, null=True, blank=True)
    close_price = models.DecimalField("قیمت پایانی", max_digits=15, decimal_places=2, null=True, blank=True)
    first_price = models.DecimalField("قیمت اول", max_digits=15, decimal_places=2, null=True, blank=True)
    min_price = models.DecimalField("کمترین قیمت", max_digits=15, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField("بیشترین قیمت", max_digits=15, decimal_places=2, null=True, blank=True)
    yesterday_price = models.DecimalField("قیمت دیروز", max_digits=15, decimal_places=2, null=True, blank=True)
    
    # اطلاعات حجم و ارزش
    trade_count = models.IntegerField("تعداد معامله", null=True, blank=True)
    trade_volume = models.BigIntegerField("حجم معامله", null=True, blank=True)
    trade_value = models.BigIntegerField("ارزش معامله", null=True, blank=True)
    
    # تاریخ و زمان
    trade_date_shamsi = models.CharField("تاریخ شمسی", max_length=10, null=True, blank=True)
    trade_date_gregorian = models.DateField("تاریخ میلادی", null=True, blank=True)
    
    # سایر اطلاعات
    market_code = models.CharField("کد بازار", max_length=10, null=True, blank=True)
    group_code = models.CharField("کد گروه", max_length=10, null=True, blank=True)
    state = models.CharField("وضعیت", max_length=20, null=True, blank=True)
    
    # متادیتا
    created_at = models.DateTimeField("زمان ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("زمان به‌روزرسانی", auto_now=True)
    
    # JSON field برای ذخیره داده‌های خام کامل
    raw_data = models.JSONField("داده‌های خام", null=True, blank=True)
    
    class Meta:
        verbose_name = "داده خام"
        verbose_name_plural = "تمام داده‌ها (All Data)"
        ordering = ['-trade_date_gregorian', 'symbol_code']
        db_table = 'data_management_all_data'
        indexes = [
            models.Index(fields=['symbol_code', 'trade_date_gregorian']),
            models.Index(fields=['trade_date_gregorian']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.symbol_name or 'نامشخص'} - {self.trade_date_shamsi or 'تاریخ نامشخص'}"


class BaseAggregatedData(models.Model):
    """مدل پایه برای داده‌های تجمیعی"""
    
    # قیمت‌ها
    avg_weighted_final_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="قیمت پایانی میانگین موزون"
    )
    avg_final_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="میانگین قیمت پایانی"
    )
    min_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="پایین‌ترین قیمت"
    )
    max_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="بالاترین قیمت"
    )
    avg_base_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="میانگین قیمت پایه عرضه"
    )
    
    # حجم‌ها
    total_contracts_volume = models.DecimalField(
        max_digits=20, decimal_places=2, default=0,
        verbose_name="جمع حجم قراردادها"
    )
    total_supply_volume = models.DecimalField(
        max_digits=20, decimal_places=2, default=0,
        verbose_name="جمع حجم عرضه"
    )
    total_demand_volume = models.DecimalField(
        max_digits=20, decimal_places=2, default=0,
        verbose_name="جمع حجم تقاضا"
    )
    
    # ارزش معاملات
    total_trade_value = models.DecimalField(
        max_digits=25, decimal_places=2, default=0,
        verbose_name="جمع ارزش معاملات (هزار ریال)"
    )
    
    # نسبت قدرت خریدار به فروشنده
    buyer_seller_power_ratio = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        verbose_name="نسبت قدرت خریدار به فروشنده"
    )
    
    # متادیتا
    records_count = models.IntegerField(default=0, verbose_name="تعداد رکوردهای پردازش شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    
    class Meta:
        abstract = True
        
    def calculate_buyer_seller_ratio(self):
        """محاسبه نسبت قدرت خریدار به فروشنده"""
        if self.total_supply_volume and self.total_supply_volume > 0:
            self.buyer_seller_power_ratio = self.total_demand_volume / self.total_supply_volume
        else:
            self.buyer_seller_power_ratio = None


class DailyData(BaseAggregatedData):
    """داده‌های تجمیعی روزانه"""
    
    trade_date = models.DateField(unique=True, verbose_name="تاریخ معامله")
    trade_date_shamsi = models.CharField(max_length=10, verbose_name="تاریخ شمسی")
    
    class Meta:
        db_table = 'data_management_daily_data'
        verbose_name = "داده روزانه"
        verbose_name_plural = "داده‌های روزانه"
        ordering = ['-trade_date']
        
    def __str__(self):
        return f"داده روزانه {self.trade_date_shamsi}"


class WeeklyData(BaseAggregatedData):
    """داده‌های تجمیعی هفتگی"""
    
    week_start_date = models.DateField(verbose_name="تاریخ شروع هفته")
    week_end_date = models.DateField(verbose_name="تاریخ پایان هفته")
    week_start_shamsi = models.CharField(max_length=10, verbose_name="شروع هفته شمسی")
    week_end_shamsi = models.CharField(max_length=10, verbose_name="پایان هفته شمسی")
    year = models.IntegerField(verbose_name="سال")
    week_number = models.IntegerField(verbose_name="شماره هفته")
    
    class Meta:
        db_table = 'data_management_weekly_data'
        verbose_name = "داده هفتگی"
        verbose_name_plural = "داده‌های هفتگی"
        ordering = ['-year', '-week_number']
        unique_together = ['year', 'week_number']
        
    def __str__(self):
        return f"هفته {self.week_number} سال {self.year} ({self.week_start_shamsi} تا {self.week_end_shamsi})"


class MonthlyData(BaseAggregatedData):
    """داده‌های تجمیعی ماهانه"""
    
    year = models.IntegerField(verbose_name="سال")
    month = models.IntegerField(verbose_name="ماه")
    month_shamsi = models.CharField(max_length=7, verbose_name="ماه و سال شمسی")  # مثل 1404/04
    
    class Meta:
        db_table = 'data_management_monthly_data'
        verbose_name = "داده ماهانه"
        verbose_name_plural = "داده‌های ماهانه"
        ordering = ['-year', '-month']
        unique_together = ['year', 'month']
        
    def __str__(self):
        return f"ماه {self.month_shamsi}"


class YearlyData(BaseAggregatedData):
    """داده‌های تجمیعی سالانه"""
    
    year = models.IntegerField(unique=True, verbose_name="سال شمسی")
    
    class Meta:
        db_table = 'data_management_yearly_data'
        verbose_name = "داده سالانه"
        verbose_name_plural = "داده‌های سالانه"
        ordering = ['-year']
        
    def __str__(self):
        return f"سال {self.year}"


class DataAggregationLog(models.Model):
    """لاگ عملیات تجمیع داده‌ها"""
    
    AGGREGATION_TYPES = [
        ('daily', 'روزانه'),
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('yearly', 'سالانه'),
        ('all', 'همه موارد'),
    ]
    
    aggregation_type = models.CharField(
        max_length=20, choices=AGGREGATION_TYPES,
        verbose_name="نوع تجمیع"
    )
    start_time = models.DateTimeField(verbose_name="زمان شروع")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="زمان پایان")
    records_processed = models.IntegerField(default=0, verbose_name="تعداد رکوردهای پردازش شده")
    records_created = models.IntegerField(default=0, verbose_name="تعداد رکوردهای ایجاد شده")
    records_updated = models.IntegerField(default=0, verbose_name="تعداد رکوردهای بروزرسانی شده")
    success = models.BooleanField(default=False, verbose_name="موفقیت‌آمیز")
    error_message = models.TextField(blank=True, verbose_name="پیام خطا")
    
    class Meta:
        db_table = 'data_management_aggregation_log'
        verbose_name = "لاگ تجمیع داده"
        verbose_name_plural = "لاگ‌های تجمیع داده"
        ordering = ['-start_time']
        
    def __str__(self):
        status = "✅ موفق" if self.success else "❌ ناموفق"
        return f"{self.get_aggregation_type_display()} - {self.start_time.strftime('%Y/%m/%d %H:%M')} - {status}"
        
    @property
    def duration(self):
        """مدت زمان اجرا"""
        if self.end_time:
            return self.end_time - self.start_time
        return None
