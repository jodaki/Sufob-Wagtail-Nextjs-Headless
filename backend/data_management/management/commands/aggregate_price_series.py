from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Min, Max, Sum, Count
from decimal import Decimal
import jdatetime
from datetime import datetime, date

from data_management.models import (
    AllData, 
    CommodityDailyPriceSeries,
    CommodityWeeklyPriceSeries, 
    CommodityMonthlyPriceSeries,
    CommodityYearlyPriceSeries,
    DataAggregationLog
)


class Command(BaseCommand):
    help = 'تجمیع داده‌های AllData و ساخت سری‌های زمانی قیمت برای هر کالا'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            choices=['daily', 'weekly', 'monthly', 'yearly', 'all'],
            default='all',
            help='نوع دوره برای تجمیع (پیش‌فرض: all)'
        )
        parser.add_argument(
            '--commodity',
            type=str,
            help='نام کالای خاص برای پردازش (اختیاری)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='بازنویسی داده‌های موجود'
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        period = options['period']
        commodity_filter = options.get('commodity')
        force_update = options.get('force', False)
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 شروع تجمیع داده‌ها - دوره: {period}')
        )
        
        # ایجاد لاگ
        log = DataAggregationLog.objects.create(
            aggregation_type=period,
            start_time=start_time
        )
        
        try:
            total_processed = 0
            total_created = 0
            total_updated = 0
            
            if period == 'all':
                # پردازش همه دوره‌ها
                daily_stats = self.aggregate_daily_data(commodity_filter, force_update)
                weekly_stats = self.aggregate_weekly_data(commodity_filter, force_update)
                monthly_stats = self.aggregate_monthly_data(commodity_filter, force_update)
                yearly_stats = self.aggregate_yearly_data(commodity_filter, force_update)
                
                total_processed = sum([s[0] for s in [daily_stats, weekly_stats, monthly_stats, yearly_stats]])
                total_created = sum([s[1] for s in [daily_stats, weekly_stats, monthly_stats, yearly_stats]])
                total_updated = sum([s[2] for s in [daily_stats, weekly_stats, monthly_stats, yearly_stats]])
                
            elif period == 'daily':
                total_processed, total_created, total_updated = self.aggregate_daily_data(commodity_filter, force_update)
            elif period == 'weekly':
                total_processed, total_created, total_updated = self.aggregate_weekly_data(commodity_filter, force_update)
            elif period == 'monthly':
                total_processed, total_created, total_updated = self.aggregate_monthly_data(commodity_filter, force_update)
            elif period == 'yearly':
                total_processed, total_created, total_updated = self.aggregate_yearly_data(commodity_filter, force_update)
            
            # به‌روزرسانی لاگ
            log.end_time = timezone.now()
            log.records_processed = total_processed
            log.records_created = total_created
            log.records_updated = total_updated
            log.success = True
            log.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ تجمیع با موفقیت انجام شد!\n'
                    f'   پردازش شده: {total_processed:,}\n'
                    f'   ایجاد شده: {total_created:,}\n'
                    f'   بروزرسانی شده: {total_updated:,}\n'
                    f'   مدت زمان: {log.duration}'
                )
            )
            
        except Exception as e:
            log.end_time = timezone.now()
            log.success = False
            log.error_message = str(e)
            log.save()
            
            self.stdout.write(
                self.style.ERROR(f'❌ خطا در تجمیع داده‌ها: {e}')
            )
            raise

    def get_commodities_list(self, commodity_filter=None):
        """دریافت لیست کالاهای موجود"""
        queryset = AllData.objects.exclude(
            commodity_name__isnull=True
        ).exclude(
            commodity_name__exact=''
        ).values_list('commodity_name', flat=True).distinct()
        
        if commodity_filter:
            queryset = queryset.filter(commodity_name__icontains=commodity_filter)
            
        return list(queryset)

    def get_valid_alldata_queryset(self, commodity_name):
        """دریافت داده‌های معتبر AllData برای یک کالا"""
        return AllData.objects.filter(
            commodity_name=commodity_name,
            final_price__isnull=False,
            final_price__gt=0,
            contract_volume__isnull=False,
            contract_volume__gt=0
        ).exclude(transaction_date__isnull=True).exclude(transaction_date__exact='')

    def parse_jalali_date(self, jalali_str):
        """تبدیل تاریخ شمسی به میلادی"""
        try:
            if not jalali_str or len(jalali_str) < 8:
                return None
            
            # فرمت معمول: YYYY/MM/DD یا YYYY-MM-DD
            jalali_str = jalali_str.replace('-', '/').strip()
            parts = jalali_str.split('/')
            
            if len(parts) == 3:
                jy, jm, jd = int(parts[0]), int(parts[1]), int(parts[2])
                return jdatetime.date(jy, jm, jd).togregorian()
        except Exception:
            pass
        return None

    def aggregate_daily_data(self, commodity_filter=None, force_update=False):
        """تجمیع داده‌های روزانه"""
        self.stdout.write('📅 پردازش داده‌های روزانه...')
        
        commodities = self.get_commodities_list(commodity_filter)
        processed = 0
        created = 0
        updated = 0
        
        for commodity in commodities:
            self.stdout.write(f'   کالا: {commodity}')
            
            # گروه‌بندی بر اساس تاریخ
            daily_groups = {}
            valid_data = self.get_valid_alldata_queryset(commodity)
            
            for item in valid_data:
                gregorian_date = self.parse_jalali_date(item.transaction_date)
                if gregorian_date:
                    date_key = gregorian_date
                    if date_key not in daily_groups:
                        daily_groups[date_key] = []
                    daily_groups[date_key].append(item)
            
            # ایجاد یا بروزرسانی رکوردهای روزانه
            for trade_date, items in daily_groups.items():
                prices = [float(item.final_price) for item in items]
                volumes = [item.contract_volume for item in items if item.contract_volume]
                
                if prices and volumes:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    total_volume = sum(volumes)
                    transaction_count = len(items)
                    
                    # تاریخ شمسی
                    jalali_date = jdatetime.date.fromgregorian(date=trade_date)
                    trade_date_shamsi = jalali_date.strftime('%Y/%m/%d')
                    
                    # ایجاد یا بروزرسانی
                    obj, is_created = CommodityDailyPriceSeries.objects.update_or_create(
                        commodity_name=commodity,
                        trade_date=trade_date,
                        defaults={
                            'trade_date_shamsi': trade_date_shamsi,
                            'avg_price': Decimal(str(round(avg_price, 2))),
                            'min_price': Decimal(str(round(min_price, 2))),
                            'max_price': Decimal(str(round(max_price, 2))),
                            'total_volume': total_volume,
                            'transaction_count': transaction_count,
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                    processed += 1
        
        self.stdout.write(f'   ✅ روزانه: {processed:,} پردازش، {created:,} ایجاد، {updated:,} بروزرسانی')
        return processed, created, updated

    def aggregate_weekly_data(self, commodity_filter=None, force_update=False):
        """تجمیع داده‌های هفتگی"""
        self.stdout.write('📊 پردازش داده‌های هفتگی...')
        
        commodities = self.get_commodities_list(commodity_filter)
        processed = 0
        created = 0
        updated = 0
        
        for commodity in commodities:
            # گروه‌بندی بر اساس سال و هفته
            weekly_groups = {}
            valid_data = self.get_valid_alldata_queryset(commodity)
            
            for item in valid_data:
                gregorian_date = self.parse_jalali_date(item.transaction_date)
                if gregorian_date:
                    year, week, _ = gregorian_date.isocalendar()
                    week_key = (year, week)
                    if week_key not in weekly_groups:
                        weekly_groups[week_key] = []
                    weekly_groups[week_key].append(item)
            
            # ایجاد رکوردهای هفتگی
            for (year, week_num), items in weekly_groups.items():
                prices = [float(item.final_price) for item in items]
                volumes = [item.contract_volume for item in items if item.contract_volume]
                
                if prices and volumes:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    total_volume = sum(volumes)
                    transaction_count = len(items)
                    
                    # محاسبه تاریخ شروع و پایان هفته
                    week_start = date.fromisocalendar(year, week_num, 1)
                    week_end = date.fromisocalendar(year, week_num, 7)
                    
                    obj, is_created = CommodityWeeklyPriceSeries.objects.update_or_create(
                        commodity_name=commodity,
                        year=year,
                        week_number=week_num,
                        defaults={
                            'week_start_date': week_start,
                            'week_end_date': week_end,
                            'avg_price': Decimal(str(round(avg_price, 2))),
                            'min_price': Decimal(str(round(min_price, 2))),
                            'max_price': Decimal(str(round(max_price, 2))),
                            'total_volume': total_volume,
                            'transaction_count': transaction_count,
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                    processed += 1
        
        self.stdout.write(f'   ✅ هفتگی: {processed:,} پردازش، {created:,} ایجاد، {updated:,} بروزرسانی')
        return processed, created, updated

    def aggregate_monthly_data(self, commodity_filter=None, force_update=False):
        """تجمیع داده‌های ماهانه"""
        self.stdout.write('📆 پردازش داده‌های ماهانه...')
        
        commodities = self.get_commodities_list(commodity_filter)
        processed = 0
        created = 0
        updated = 0
        
        for commodity in commodities:
            # گروه‌بندی بر اساس سال و ماه
            monthly_groups = {}
            valid_data = self.get_valid_alldata_queryset(commodity)
            
            for item in valid_data:
                gregorian_date = self.parse_jalali_date(item.transaction_date)
                if gregorian_date:
                    # تبدیل به شمسی برای دریافت سال و ماه شمسی
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    month_key = (jalali_date.year, jalali_date.month)
                    if month_key not in monthly_groups:
                        monthly_groups[month_key] = []
                    monthly_groups[month_key].append(item)
            
            # ایجاد رکوردهای ماهانه
            for (year, month), items in monthly_groups.items():
                prices = [float(item.final_price) for item in items]
                volumes = [item.contract_volume for item in items if item.contract_volume]
                
                if prices and volumes:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    total_volume = sum(volumes)
                    transaction_count = len(items)
                    
                    month_shamsi = f"{year}/{month:02d}"
                    
                    obj, is_created = CommodityMonthlyPriceSeries.objects.update_or_create(
                        commodity_name=commodity,
                        year=year,
                        month=month,
                        defaults={
                            'month_shamsi': month_shamsi,
                            'avg_price': Decimal(str(round(avg_price, 2))),
                            'min_price': Decimal(str(round(min_price, 2))),
                            'max_price': Decimal(str(round(max_price, 2))),
                            'total_volume': total_volume,
                            'transaction_count': transaction_count,
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                    processed += 1
        
        self.stdout.write(f'   ✅ ماهانه: {processed:,} پردازش، {created:,} ایجاد، {updated:,} بروزرسانی')
        return processed, created, updated

    def aggregate_yearly_data(self, commodity_filter=None, force_update=False):
        """تجمیع داده‌های سالانه"""
        self.stdout.write('📈 پردازش داده‌های سالانه...')
        
        commodities = self.get_commodities_list(commodity_filter)
        processed = 0
        created = 0
        updated = 0
        
        for commodity in commodities:
            # گروه‌بندی بر اساس سال شمسی
            yearly_groups = {}
            valid_data = self.get_valid_alldata_queryset(commodity)
            
            for item in valid_data:
                gregorian_date = self.parse_jalali_date(item.transaction_date)
                if gregorian_date:
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    year_key = jalali_date.year
                    if year_key not in yearly_groups:
                        yearly_groups[year_key] = []
                    yearly_groups[year_key].append(item)
            
            # ایجاد رکوردهای سالانه
            for year, items in yearly_groups.items():
                prices = [float(item.final_price) for item in items]
                volumes = [item.contract_volume for item in items if item.contract_volume]
                
                if prices and volumes:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    total_volume = sum(volumes)
                    transaction_count = len(items)
                    
                    obj, is_created = CommodityYearlyPriceSeries.objects.update_or_create(
                        commodity_name=commodity,
                        year=year,
                        defaults={
                            'avg_price': Decimal(str(round(avg_price, 2))),
                            'min_price': Decimal(str(round(min_price, 2))),
                            'max_price': Decimal(str(round(max_price, 2))),
                            'total_volume': total_volume,
                            'transaction_count': transaction_count,
                        }
                    )
                    
                    if is_created:
                        created += 1
                    else:
                        updated += 1
                    processed += 1
        
        self.stdout.write(f'   ✅ سالانه: {processed:,} پردازش، {created:,} ایجاد، {updated:,} بروزرسانی')
        return processed, created, updated
