from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg, Sum, Min, Max, Count
from django.utils import timezone
from decimal import Decimal
import jdatetime
from datetime import datetime, timedelta

from .models import AllData, DailyData, WeeklyData, MonthlyData, YearlyData, DataAggregationLog


def shamsi_to_gregorian(shamsi_date_str):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        if not shamsi_date_str or len(shamsi_date_str) != 10:
            return None
        year, month, day = map(int, shamsi_date_str.split('/'))
        jd = jdatetime.date(year, month, day)
        return jd.togregorian()
    except:
        return None


def gregorian_to_shamsi(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    try:
        jd = jdatetime.date.fromgregorian(date=gregorian_date)
        return jd.strftime('%Y/%m/%d')
    except:
        return None


@receiver(post_save, sender=AllData)
def auto_aggregate_data(sender, instance, created, **kwargs):
    """تجمیع خودکار داده‌ها بعد از ذخیره AllData"""
    if created and instance.transaction_date:
        # فقط برای رکوردهای جدید و با تاریخ معتبر
        
        # شروع لاگ تجمیع
        log = DataAggregationLog.objects.create(
            aggregation_type='all',
            start_time=timezone.now()
        )
        
        try:
            gregorian_date = shamsi_to_gregorian(instance.transaction_date)
            if gregorian_date:
                
                # 1. تجمیع روزانه
                aggregate_daily_data(gregorian_date, instance.transaction_date)
                
                # 2. تجمیع هفتگی
                aggregate_weekly_data(gregorian_date)
                
                # 3. تجمیع ماهانه
                aggregate_monthly_data(gregorian_date)
                
                # 4. تجمیع سالانه
                aggregate_yearly_data(gregorian_date)
                
                # پایان موفق لاگ
                log.end_time = timezone.now()
                log.success = True
                log.records_processed = 1
                log.save()
                
        except Exception as e:
            # خطا در تجمیع
            log.end_time = timezone.now()
            log.success = False
            log.error_message = str(e)
            log.save()


def aggregate_daily_data(date_gregorian, date_shamsi=None, force=False):
    """تجمیع داده‌های روزانه"""
    
    # اگر تاریخ شمسی داده نشده، آن را محاسبه کن
    if not date_shamsi:
        date_shamsi = gregorian_to_shamsi(date_gregorian)
    
    # بررسی اینکه آیا قبلاً تجمیع شده یا نه
    if not force and DailyData.objects.filter(trade_date=date_gregorian).exists():
        return
    
    # دریافت تمام داده‌های آن روز
    daily_records = AllData.objects.filter(transaction_date=date_shamsi)
    
    if not daily_records.exists():
        return
    
    # محاسبه آمارها
    aggregates = daily_records.aggregate(
        avg_final_price=Avg('final_price'),
        min_price=Min('lowest_price'),
        max_price=Max('highest_price'),
        avg_base_price=Avg('base_price'),
        total_contracts_volume=Sum('contract_volume'),
        total_supply_volume=Sum('offer_volume'),
        total_demand_volume=Sum('demand_volume'),
        total_trade_value=Sum('transaction_value'),
        records_count=Count('id')
    )
    
    # محاسبه میانگین موزون قیمت نهایی (بر اساس حجم)
    weighted_sum = 0
    total_volume = 0
    for record in daily_records:
        if record.final_price and record.contract_volume:
            weighted_sum += float(record.final_price) * record.contract_volume
            total_volume += record.contract_volume
    
    avg_weighted_final_price = Decimal(weighted_sum / total_volume) if total_volume > 0 else None
    
    # ایجاد یا بروزرسانی رکورد روزانه
    daily_data, created = DailyData.objects.update_or_create(
        trade_date=date_gregorian,
        defaults={
            'trade_date_shamsi': date_shamsi,
            'avg_weighted_final_price': avg_weighted_final_price,
            'avg_final_price': aggregates['avg_final_price'],
            'min_price': aggregates['min_price'],
            'max_price': aggregates['max_price'],
            'avg_base_price': aggregates['avg_base_price'],
            'total_contracts_volume': aggregates['total_contracts_volume'] or 0,
            'total_supply_volume': aggregates['total_supply_volume'] or 0,
            'total_demand_volume': aggregates['total_demand_volume'] or 0,
            'total_trade_value': aggregates['total_trade_value'] or 0,
            'records_count': aggregates['records_count'],
        }
    )
    
    # محاسبه نسبت قدرت خریدار به فروشنده
    daily_data.calculate_buyer_seller_ratio()
    daily_data.save()


def aggregate_weekly_data(date_gregorian, force=False):
    """تجمیع داده‌های هفتگی"""
    
    # پیدا کردن شروع و پایان هفته
    days_since_saturday = (date_gregorian.weekday() + 2) % 7  # شنبه = 0
    week_start = date_gregorian - timedelta(days=days_since_saturday)
    week_end = week_start + timedelta(days=6)
    
    # بررسی اینکه آیا قبلاً تجمیع شده یا نه
    if not force and WeeklyData.objects.filter(
        week_start_date=week_start,
        week_end_date=week_end
    ).exists():
        return
    
    # تعیین سال و شماره هفته شمسی
    shamsi_date = jdatetime.date.fromgregorian(date=date_gregorian)
    year = shamsi_date.year
    week_number = shamsi_date.isocalendar()[1]
    
    # دریافت داده‌های روزانه آن هفته
    weekly_records = DailyData.objects.filter(
        trade_date__range=[week_start, week_end]
    )
    
    if not weekly_records.exists():
        return
    
    # محاسبه آمارها
    aggregates = weekly_records.aggregate(
        avg_final_price=Avg('avg_final_price'),
        min_price=Min('min_price'),
        max_price=Max('max_price'),
        avg_base_price=Avg('avg_base_price'),
        total_contracts_volume=Sum('total_contracts_volume'),
        total_supply_volume=Sum('total_supply_volume'),
        total_demand_volume=Sum('total_demand_volume'),
        total_trade_value=Sum('total_trade_value'),
        records_count=Sum('records_count')
    )
    
    # ایجاد یا بروزرسانی رکورد هفتگی
    weekly_data, created = WeeklyData.objects.update_or_create(
        year=year,
        week_number=week_number,
        defaults={
            'week_start_date': week_start,
            'week_end_date': week_end,
            'week_start_shamsi': gregorian_to_shamsi(week_start),
            'week_end_shamsi': gregorian_to_shamsi(week_end),
            'avg_final_price': aggregates['avg_final_price'],
            'min_price': aggregates['min_price'],
            'max_price': aggregates['max_price'],
            'avg_base_price': aggregates['avg_base_price'],
            'total_contracts_volume': aggregates['total_contracts_volume'] or 0,
            'total_supply_volume': aggregates['total_supply_volume'] or 0,
            'total_demand_volume': aggregates['total_demand_volume'] or 0,
            'total_trade_value': aggregates['total_trade_value'] or 0,
            'records_count': aggregates['records_count'] or 0,
        }
    )
    
    weekly_data.calculate_buyer_seller_ratio()
    weekly_data.save()


def aggregate_monthly_data(date_gregorian, force=False):
    """تجمیع داده‌های ماهانه"""
    
    shamsi_date = jdatetime.date.fromgregorian(date=date_gregorian)
    year = shamsi_date.year
    month = shamsi_date.month
    month_shamsi = f"{year}/{month:02d}"
    
    # بررسی اینکه آیا قبلاً تجمیع شده یا نه
    if not force and MonthlyData.objects.filter(
        month_shamsi=month_shamsi
    ).exists():
        return
    
    # دریافت داده‌های روزانه آن ماه
    monthly_records = DailyData.objects.filter(
        trade_date__year=date_gregorian.year,
        trade_date__month=date_gregorian.month
    )
    
    if not monthly_records.exists():
        return
    
    # محاسبه آمارها
    aggregates = monthly_records.aggregate(
        avg_final_price=Avg('avg_final_price'),
        min_price=Min('min_price'),
        max_price=Max('max_price'),
        avg_base_price=Avg('avg_base_price'),
        total_contracts_volume=Sum('total_contracts_volume'),
        total_supply_volume=Sum('total_supply_volume'),
        total_demand_volume=Sum('total_demand_volume'),
        total_trade_value=Sum('total_trade_value'),
        records_count=Sum('records_count')
    )
    
    # ایجاد یا بروزرسانی رکورد ماهانه
    monthly_data, created = MonthlyData.objects.update_or_create(
        year=year,
        month=month,
        defaults={
            'month_shamsi': month_shamsi,
            'avg_final_price': aggregates['avg_final_price'],
            'min_price': aggregates['min_price'],
            'max_price': aggregates['max_price'],
            'avg_base_price': aggregates['avg_base_price'],
            'total_contracts_volume': aggregates['total_contracts_volume'] or 0,
            'total_supply_volume': aggregates['total_supply_volume'] or 0,
            'total_demand_volume': aggregates['total_demand_volume'] or 0,
            'total_trade_value': aggregates['total_trade_value'] or 0,
            'records_count': aggregates['records_count'] or 0,
        }
    )
    
    monthly_data.calculate_buyer_seller_ratio()
    monthly_data.save()


def aggregate_yearly_data(date_gregorian, force=False):
    """تجمیع داده‌های سالانه"""
    
    shamsi_date = jdatetime.date.fromgregorian(date=date_gregorian)
    year = shamsi_date.year
    
    # بررسی اینکه آیا قبلاً تجمیع شده یا نه
    if not force and YearlyData.objects.filter(year=year).exists():
        return
    
    # دریافت داده‌های ماهانه آن سال
    yearly_records = MonthlyData.objects.filter(year=year)
    
    if not yearly_records.exists():
        return
    
    # محاسبه آمارها
    aggregates = yearly_records.aggregate(
        avg_final_price=Avg('avg_final_price'),
        min_price=Min('min_price'),
        max_price=Max('max_price'),
        avg_base_price=Avg('avg_base_price'),
        total_contracts_volume=Sum('total_contracts_volume'),
        total_supply_volume=Sum('total_supply_volume'),
        total_demand_volume=Sum('total_demand_volume'),
        total_trade_value=Sum('total_trade_value'),
        records_count=Sum('records_count')
    )
    
    # ایجاد یا بروزرسانی رکورد سالانه
    yearly_data, created = YearlyData.objects.update_or_create(
        year=year,
        defaults={
            'avg_final_price': aggregates['avg_final_price'],
            'min_price': aggregates['min_price'],
            'max_price': aggregates['max_price'],
            'avg_base_price': aggregates['avg_base_price'],
            'total_contracts_volume': aggregates['total_contracts_volume'] or 0,
            'total_supply_volume': aggregates['total_supply_volume'] or 0,
            'total_demand_volume': aggregates['total_demand_volume'] or 0,
            'total_trade_value': aggregates['total_trade_value'] or 0,
            'records_count': aggregates['records_count'] or 0,
        }
    )
    
    yearly_data.calculate_buyer_seller_ratio()
    yearly_data.save()
