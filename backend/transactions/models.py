from django.db import models

# مدل موقت برای ذخیره داده‌های استخراج‌شده
class StagedTransaction(models.Model):
    commodity_name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)
    hall = models.CharField(max_length=100)
    producer = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=50)
    final_price = models.FloatField(null=True, blank=True)
    transaction_value = models.BigIntegerField(default=0)
    lowest_price = models.FloatField(null=True, blank=True)
    highest_price = models.FloatField(null=True, blank=True)
    base_price = models.FloatField()
    offer_volume = models.IntegerField()
    demand_volume = models.IntegerField()
    contract_volume = models.IntegerField()
    unit = models.CharField(max_length=20)
    transaction_date = models.CharField(max_length=10)
    supplier = models.CharField(max_length=200)
    broker = models.CharField(max_length=100)
    settlement_type = models.CharField(max_length=50)
    delivery_date = models.CharField(max_length=10, null=True, blank=True)
    warehouse = models.CharField(max_length=100, null=True, blank=True)
    settlement_date = models.CharField(max_length=10, null=True, blank=True)
    x_talar_report_pk = models.IntegerField(unique=True, null=True, blank=True)
    b_arzeh_radif_tar_sarresid = models.CharField(max_length=10, null=True, blank=True)
    mode_description = models.CharField(max_length=50, null=True, blank=True)
    method_description = models.CharField(max_length=50, null=True, blank=True)
    currency = models.CharField(max_length=20, null=True, blank=True)
    packet_name = models.CharField(max_length=50, null=True, blank=True)
    arzeh_pk = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commodity_name} - {self.symbol} - {self.transaction_date} (staged)"
class ImportLog(models.Model):
    product_type = models.CharField(max_length=50)
    from_date = models.CharField(max_length=10)
    to_date = models.CharField(max_length=10)
    record_count = models.IntegerField()
    status = models.CharField(max_length=20)  # ذخیره شده / رد شد
    add_type = models.CharField(max_length=20)  # دستی یا اتوماتیک
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at.date()} | {self.product_type} | {self.status} | {self.record_count}"
from django.db import models

class Transaction(models.Model):
    commodity_name = models.CharField(max_length=100)  # GoodsName
    symbol = models.CharField(max_length=50)  # Symbol
    hall = models.CharField(max_length=100)  # Talar
    producer = models.CharField(max_length=200)  # ProducerName
    contract_type = models.CharField(max_length=50)  # ContractType
    final_price = models.FloatField(null=True, blank=True)  # Price
    transaction_value = models.BigIntegerField(default=0)  # TotalPrice
    lowest_price = models.FloatField(null=True, blank=True)  # MinPrice
    highest_price = models.FloatField(null=True, blank=True)  # MaxPrice
    base_price = models.FloatField()  # ArzeBasePrice
    offer_volume = models.IntegerField()  # arze
    demand_volume = models.IntegerField()  # taghaza
    contract_volume = models.IntegerField()  # Quantity
    unit = models.CharField(max_length=20)  # Unit
    transaction_date = models.CharField(max_length=10)  # date (شمسی)
    supplier = models.CharField(max_length=200)  # ArzehKonandeh
    broker = models.CharField(max_length=100)  # cBrokerSpcName
    settlement_type = models.CharField(max_length=50)  # Tasvieh
    delivery_date = models.CharField(max_length=10, null=True, blank=True)  # DeliveryDate
    warehouse = models.CharField(max_length=100, null=True, blank=True)  # Warehouse
    settlement_date = models.CharField(max_length=10, null=True, blank=True)  # SettlementDate
    x_talar_report_pk = models.IntegerField(unique=True, null=True, blank=True)  # xTalarReportPK
    b_arzeh_radif_tar_sarresid = models.CharField(max_length=10, null=True, blank=True)  # bArzehRadifTarSarresid
    mode_description = models.CharField(max_length=50, null=True, blank=True)  # ModeDescription
    method_description = models.CharField(max_length=50, null=True, blank=True)  # MethodDescription
    currency = models.CharField(max_length=20, null=True, blank=True)  # Currency
    packet_name = models.CharField(max_length=50, null=True, blank=True)  # PacketName
    arzeh_pk = models.IntegerField(null=True, blank=True)  # arzehPk

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['x_talar_report_pk'], name='unique_x_talar_report_pk')
        ]

    def __str__(self):
        return f"{self.commodity_name} - {self.symbol} - {self.transaction_date}"
class DailyInfo(models.Model):
    avg_final_price = models.CharField(max_length=20)
    final_price = models.CharField(max_length=20)
    lowest_price = models.CharField(max_length=20)
    highest_price = models.CharField(max_length=20)
    weekly_range = models.CharField(max_length=30)
    monthly_range = models.CharField(max_length=30)
    monthly_change = models.CharField(max_length=20)
    settlement_type = models.CharField(max_length=20)
    transaction_date = models.CharField(max_length=10)
    contract_volume = models.CharField(max_length=20)
    demand = models.CharField(max_length=20)
    offer_volume = models.CharField(max_length=20)
    base_price = models.CharField(max_length=20)
    transaction_value = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_date} | {self.final_price}"