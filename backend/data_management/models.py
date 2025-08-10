from django.db import models
from django.utils import timezone
import jdatetime


class AllData(models.Model):
    """تمام داده‌های خام استخراج شده از API بورس"""
    
    # اطلاعات اصلی
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا", blank=True)
    symbol = models.CharField(max_length=50, verbose_name="نماد", blank=True)
    hall = models.CharField(max_length=100, verbose_name="تالار", blank=True)
    producer = models.CharField(max_length=200, verbose_name="تولیدکننده", blank=True)
    contract_type = models.CharField(max_length=50, verbose_name="نوع قرارداد", blank=True)
    
    # قیمت‌ها - استفاده از DecimalField برای دقت بیشتر
    final_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت نهایی")
    transaction_value = models.BigIntegerField(null=True, blank=True, default=0, verbose_name="ارزش معامله")
    lowest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="کمترین قیمت")
    highest_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="بیشترین قیمت")
    base_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="قیمت پایه")
    
    # حجم‌ها
    offer_volume = models.IntegerField(default=0, verbose_name="حجم عرضه")
    demand_volume = models.IntegerField(default=0, verbose_name="حجم تقاضا")
    contract_volume = models.IntegerField(null=True, blank=True, default=0, verbose_name="حجم قرارداد")
    unit = models.CharField(max_length=20, verbose_name="واحد", blank=True)
    
    # تاریخ
    transaction_date = models.CharField(max_length=10, verbose_name="تاریخ معامله شمسی", blank=True)
    
    # اطلاعات اضافی
    supplier = models.CharField(max_length=200, verbose_name="عرضه‌کننده", blank=True)
    broker = models.CharField(max_length=100, verbose_name="کارگزار", blank=True)
    settlement_type = models.CharField(max_length=50, verbose_name="نحوه تسویه", blank=True)
    delivery_date = models.CharField(max_length=10, null=True, blank=True, verbose_name="تاریخ تحویل")
    warehouse = models.CharField(max_length=100, null=True, blank=True, verbose_name="انبار")
    settlement_date = models.CharField(max_length=10, null=True, blank=True, verbose_name="تاریخ تسویه")
    
    # شناسه‌ها
    x_talar_report_pk = models.IntegerField(null=True, blank=True, verbose_name="شناسه گزارش تالار")
    b_arzeh_radif_tar_sarresid = models.CharField(max_length=10, null=True, blank=True)
    mode_description = models.CharField(max_length=50, null=True, blank=True, verbose_name="شرح روش")
    method_description = models.CharField(max_length=50, null=True, blank=True, verbose_name="شرح نحوه")
    currency = models.CharField(max_length=20, null=True, blank=True, verbose_name="ارز")
    packet_name = models.CharField(max_length=50, null=True, blank=True, verbose_name="نام بسته")
    arzeh_pk = models.IntegerField(null=True, blank=True, verbose_name="شناسه عرضه")
    
    # داده خام
    raw_data = models.JSONField(null=True, blank=True, verbose_name="داده خام")
    
    # متادیتا
    source = models.CharField(max_length=100, default="scroll-time", verbose_name="منبع داده")
    api_endpoint = models.CharField(max_length=200, null=True, blank=True, verbose_name="نقطه انتهایی API")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    
    class Meta:
        db_table = 'data_management_all_data'
        verbose_name = "تمام داده‌ها"
        verbose_name_plural = "تمام داده‌ها"
        ordering = ['-transaction_date', 'symbol']
        # اضافه کردن ایندکس‌های بهینه
        indexes = [
            models.Index(fields=['commodity_name', 'transaction_date']),
            models.Index(fields=['symbol', 'transaction_date']),
            models.Index(fields=['source', 'created_at']),
            models.Index(fields=['producer']),
            models.Index(fields=['transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.commodity_name or self.symbol} - {self.transaction_date}"


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


# مدل‌های جدید برای سری‌های زمانی کالاها

class CommodityDailyPriceSeries(models.Model):
    """سری‌های قیمت روزانه هر کالا"""
    
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا")
    trade_date = models.DateField(verbose_name="تاریخ معامله")
    trade_date_shamsi = models.CharField(max_length=10, verbose_name="تاریخ شمسی")
    
    # قیمت‌ها (فقط از final_price استفاده می‌کنیم)
    avg_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="میانگین قیمت نهایی"
    )
    min_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="کمترین قیمت"
    )
    max_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="بیشترین قیمت"
    )
    
    # حجم‌ها
    total_volume = models.BigIntegerField(default=0, verbose_name="مجموع حجم معاملات")
    transaction_count = models.IntegerField(default=0, verbose_name="تعداد معاملات")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commodity_daily_price_series'
        verbose_name = "سری قیمت روزانه کالا"
        verbose_name_plural = "سری‌های قیمت روزانه کالاها"
        unique_together = ['commodity_name', 'trade_date']
        ordering = ['-trade_date', 'commodity_name']
        indexes = [
            models.Index(fields=['commodity_name', 'trade_date']),
            models.Index(fields=['trade_date']),
        ]
        
    def __str__(self):
        return f"{self.commodity_name} - {self.trade_date_shamsi}"


class CommodityWeeklyPriceSeries(models.Model):
    """سری‌های قیمت هفتگی هر کالا"""
    
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا")
    year = models.IntegerField(verbose_name="سال")
    week_number = models.IntegerField(verbose_name="شماره هفته")
    week_start_date = models.DateField(verbose_name="تاریخ شروع هفته")
    week_end_date = models.DateField(verbose_name="تاریخ پایان هفته")
    
    # قیمت‌ها
    avg_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="میانگین قیمت نهایی"
    )
    min_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="کمترین قیمت"
    )
    max_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="بیشترین قیمت"
    )
    
    # حجم‌ها
    total_volume = models.BigIntegerField(default=0, verbose_name="مجموع حجم معاملات")
    transaction_count = models.IntegerField(default=0, verbose_name="تعداد معاملات")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commodity_weekly_price_series'
        verbose_name = "سری قیمت هفتگی کالا"
        verbose_name_plural = "سری‌های قیمت هفتگی کالاها"
        unique_together = ['commodity_name', 'year', 'week_number']
        ordering = ['-year', '-week_number', 'commodity_name']
        
    def __str__(self):
        return f"{self.commodity_name} - هفته {self.week_number} سال {self.year}"


class CommodityMonthlyPriceSeries(models.Model):
    """سری‌های قیمت ماهانه هر کالا"""
    
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا")
    year = models.IntegerField(verbose_name="سال")
    month = models.IntegerField(verbose_name="ماه")
    month_shamsi = models.CharField(max_length=7, verbose_name="ماه و سال شمسی")
    
    # قیمت‌ها
    avg_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="میانگین قیمت نهایی"
    )
    min_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="کمترین قیمت"
    )
    max_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="بیشترین قیمت"
    )
    
    # حجم‌ها
    total_volume = models.BigIntegerField(default=0, verbose_name="مجموع حجم معاملات")
    transaction_count = models.IntegerField(default=0, verbose_name="تعداد معاملات")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commodity_monthly_price_series'
        verbose_name = "سری قیمت ماهانه کالا"
        verbose_name_plural = "سری‌های قیمت ماهانه کالاها"
        unique_together = ['commodity_name', 'year', 'month']
        ordering = ['-year', '-month', 'commodity_name']
        
    def __str__(self):
        return f"{self.commodity_name} - {self.month_shamsi}"


class CommodityYearlyPriceSeries(models.Model):
    """سری‌های قیمت سالانه هر کالا"""
    
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا")
    year = models.IntegerField(verbose_name="سال شمسی")
    
    # قیمت‌ها
    avg_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="میانگین قیمت نهایی"
    )
    min_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="کمترین قیمت"
    )
    max_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="بیشترین قیمت"
    )
    
    # حجم‌ها
    total_volume = models.BigIntegerField(default=0, verbose_name="مجموع حجم معاملات")
    transaction_count = models.IntegerField(default=0, verbose_name="تعداد معاملات")
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commodity_yearly_price_series'
        verbose_name = "سری قیمت سالانه کالا"
        verbose_name_plural = "سری‌های قیمت سالانه کالاها"
        unique_together = ['commodity_name', 'year']
        ordering = ['-year', 'commodity_name']
        
    def __str__(self):
        return f"{self.commodity_name} - سال {self.year}"


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
