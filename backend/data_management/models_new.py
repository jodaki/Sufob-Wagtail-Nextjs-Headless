from django.db import models
from django.utils import timezone

class AllData(models.Model):
    """تمام داده‌های خام استخراج شده از API بورس"""
    
    # اطلاعات اصلی
    commodity_name = models.CharField(max_length=100, verbose_name="نام کالا", blank=True)
    symbol = models.CharField(max_length=50, verbose_name="نماد", blank=True)
    hall = models.CharField(max_length=100, verbose_name="تالار", blank=True)
    producer = models.CharField(max_length=200, verbose_name="تولیدکننده", blank=True)
    contract_type = models.CharField(max_length=50, verbose_name="نوع قرارداد", blank=True)
    
    # قیمت‌ها
    final_price = models.FloatField(null=True, blank=True, verbose_name="قیمت نهایی")
    transaction_value = models.BigIntegerField(default=0, verbose_name="ارزش معامله")
    lowest_price = models.FloatField(null=True, blank=True, verbose_name="کمترین قیمت")
    highest_price = models.FloatField(null=True, blank=True, verbose_name="بیشترین قیمت")
    base_price = models.FloatField(null=True, blank=True, verbose_name="قیمت پایه")
    
    # حجم‌ها
    offer_volume = models.IntegerField(default=0, verbose_name="حجم عرضه")
    demand_volume = models.IntegerField(default=0, verbose_name="حجم تقاضا")
    contract_volume = models.IntegerField(default=0, verbose_name="حجم قرارداد")
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
    
    def __str__(self):
        return f"{self.commodity_name or self.symbol} - {self.transaction_date}"
