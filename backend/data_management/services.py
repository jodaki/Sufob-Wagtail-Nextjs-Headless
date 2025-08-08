from django.db import models
from django.db.models import Avg, Sum, Min, Max, Count
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date, timedelta
# import jdatetime - disabled for now
import logging

from price_models.models import PriceData
from .models import DailyData, WeeklyData, MonthlyData, YearlyData, DataAggregationLog

logger = logging.getLogger(__name__)


class DataAggregationService:
    """سرویس تجمیع داده‌ها براساس بازه‌های زمانی مختلف"""
    
    def __init__(self):
        self.logger = logger
        
    def convert_shamsi_to_gregorian(self, shamsi_date_str: str) -> date:
        """تبدیل تاریخ شمسی به میلادی"""
        try:
            year, month, day = map(int, shamsi_date_str.split('/'))
            jd = jdatetime.date(year, month, day)
            return jd.togregorian()
        except Exception as e:
            self.logger.error(f"Error converting shamsi date {shamsi_date_str}: {e}")
            return None
            
    def convert_gregorian_to_shamsi(self, gregorian_date: date) -> str:
        """تبدیل تاریخ میلادی به شمسی"""
        try:
            jd = jdatetime.date.fromgregorian(date=gregorian_date)
            return jd.strftime('%Y/%m/%d')
        except Exception as e:
            self.logger.error(f"Error converting gregorian date {gregorian_date}: {e}")
            return str(gregorian_date)

    def aggregate_daily_data(self, start_date: date = None, end_date: date = None) -> dict:
        """تجمیع داده‌های روزانه"""
        log_entry = DataAggregationLog.objects.create(
            aggregation_type='daily',
            start_time=timezone.now()
        )
        
        try:
            # تعیین بازه تاریخ
            if not start_date or not end_date:
                # اگر تاریخ مشخص نشده، آخرین 30 روز
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
            
            stats = {
                'records_processed': 0,
                'records_created': 0,
                'records_updated': 0
            }
            
            # گروه‌بندی داده‌ها براساس تاریخ
            daily_groups = PriceData.objects.filter(
                price_date__range=[start_date, end_date]
            ).values('price_date').annotate(
                avg_weighted_final_price=Avg('final_price'),  # استفاده از final_price
                avg_final_price=Avg('final_price'), 
                min_price=Min('lowest_price'),
                max_price=Max('highest_price'),
                avg_base_price=Avg('avg_price'),
                total_contracts_volume=Sum('volume'),
                total_supply_volume=Sum('volume'),
                total_demand_volume=Sum('volume'),
                total_trade_value=Sum('value'),
                records_count=Count('id')
            ).order_by('price_date')
            
            for group in daily_groups:
                trade_date = group['price_date']
                trade_date_shamsi = self.convert_gregorian_to_shamsi(trade_date)
                
                # محاسبه نسبت قدرت خریدار به فروشنده
                buyer_seller_ratio = None
                if group['total_supply_volume'] and group['total_supply_volume'] > 0:
                    buyer_seller_ratio = group['total_demand_volume'] / group['total_supply_volume']
                
                # ایجاد یا بروزرسانی رکورد
                daily_data, created = DailyData.objects.update_or_create(
                    trade_date=trade_date,
                    defaults={
                        'trade_date_shamsi': trade_date_shamsi,
                        'avg_weighted_final_price': group['avg_weighted_final_price'],
                        'avg_final_price': group['avg_final_price'],
                        'min_price': group['min_price'],
                        'max_price': group['max_price'],
                        'avg_base_price': group['avg_base_price'],
                        'total_contracts_volume': group['total_contracts_volume'] or 0,
                        'total_supply_volume': group['total_supply_volume'] or 0,
                        'total_demand_volume': group['total_demand_volume'] or 0,
                        'total_trade_value': group['total_trade_value'] or 0,
                        'buyer_seller_power_ratio': buyer_seller_ratio,
                        'records_count': group['records_count']
                    }
                )
                
                if created:
                    stats['records_created'] += 1
                else:
                    stats['records_updated'] += 1
                    
                stats['records_processed'] += 1
            
            # بروزرسانی لاگ
            log_entry.end_time = timezone.now()
            log_entry.records_processed = stats['records_processed']
            log_entry.records_created = stats['records_created']
            log_entry.records_updated = stats['records_updated']
            log_entry.success = True
            log_entry.save()
            
            return {
                'success': True,
                'message': f"تجمیع روزانه با موفقیت انجام شد. {stats['records_created']} رکورد جدید، {stats['records_updated']} رکورد بروزرسانی شد.",
                'stats': stats
            }
            
        except Exception as e:
            error_msg = f"خطا در تجمیع داده‌های روزانه: {str(e)}"
            self.logger.error(error_msg)
            
            log_entry.end_time = timezone.now()
            log_entry.error_message = error_msg
            log_entry.success = False
            log_entry.save()
            
            return {
                'success': False,
                'error': error_msg,
                'stats': stats
            }

    def aggregate_weekly_data(self, start_date: date = None, end_date: date = None) -> dict:
        """تجمیع داده‌های هفتگی"""
        log_entry = DataAggregationLog.objects.create(
            aggregation_type='weekly',
            start_time=timezone.now()
        )
        
        try:
            stats = {'records_processed': 0, 'records_created': 0, 'records_updated': 0}
            
            # گروه‌بندی داده‌های روزانه براساس هفته
            daily_data = DailyData.objects.all()
            if start_date:
                daily_data = daily_data.filter(trade_date__gte=start_date)
            if end_date:
                daily_data = daily_data.filter(trade_date__lte=end_date)
                
            # گروه‌بندی براساس هفته شمسی
            weekly_groups = {}
            for daily in daily_data:
                jd = jdatetime.date.fromgregorian(date=daily.trade_date)
                year = jd.year
                week_number = jd.isocalendar()[1]  # شماره هفته
                
                # محاسبه شروع و پایان هفته
                week_start = jd - timedelta(days=jd.weekday())
                week_end = week_start + timedelta(days=6)
                
                week_key = f"{year}-{week_number}"
                
                if week_key not in weekly_groups:
                    weekly_groups[week_key] = {
                        'year': year,
                        'week_number': week_number,
                        'week_start_date': week_start.togregorian(),
                        'week_end_date': week_end.togregorian(),
                        'week_start_shamsi': week_start.strftime('%Y/%m/%d'),
                        'week_end_shamsi': week_end.strftime('%Y/%m/%d'),
                        'daily_records': []
                    }
                
                weekly_groups[week_key]['daily_records'].append(daily)
            
            # تجمیع داده‌ها برای هر هفته
            for week_data in weekly_groups.values():
                records = week_data['daily_records']
                
                # محاسبه آمار تجمیعی
                total_trade_value = sum(r.total_trade_value or 0 for r in records)
                total_contracts_volume = sum(r.total_contracts_volume or 0 for r in records)
                total_supply_volume = sum(r.total_supply_volume or 0 for r in records)
                total_demand_volume = sum(r.total_demand_volume or 0 for r in records)
                
                # میانگین‌ها
                avg_weighted_final_price = sum(r.avg_weighted_final_price or 0 for r in records) / len(records) if records else 0
                avg_final_price = sum(r.avg_final_price or 0 for r in records) / len(records) if records else 0
                avg_base_price = sum(r.avg_base_price or 0 for r in records) / len(records) if records else 0
                
                # حداقل و حداکثر
                min_price = min((r.min_price for r in records if r.min_price), default=0)
                max_price = max((r.max_price for r in records if r.max_price), default=0)
                
                # نسبت قدرت خریدار به فروشنده
                buyer_seller_ratio = total_demand_volume / total_supply_volume if total_supply_volume > 0 else None
                
                # ایجاد یا بروزرسانی رکورد هفتگی
                weekly_data_obj, created = WeeklyData.objects.update_or_create(
                    year=week_data['year'],
                    week_number=week_data['week_number'],
                    defaults={
                        'week_start_date': week_data['week_start_date'],
                        'week_end_date': week_data['week_end_date'],
                        'week_start_shamsi': week_data['week_start_shamsi'],
                        'week_end_shamsi': week_data['week_end_shamsi'],
                        'avg_weighted_final_price': avg_weighted_final_price,
                        'avg_final_price': avg_final_price,
                        'min_price': min_price,
                        'max_price': max_price,
                        'avg_base_price': avg_base_price,
                        'total_contracts_volume': total_contracts_volume,
                        'total_supply_volume': total_supply_volume,
                        'total_demand_volume': total_demand_volume,
                        'total_trade_value': total_trade_value,
                        'buyer_seller_power_ratio': buyer_seller_ratio,
                        'records_count': len(records)
                    }
                )
                
                if created:
                    stats['records_created'] += 1
                else:
                    stats['records_updated'] += 1
                    
                stats['records_processed'] += 1
            
            # بروزرسانی لاگ
            log_entry.end_time = timezone.now()
            log_entry.records_processed = stats['records_processed']
            log_entry.records_created = stats['records_created']
            log_entry.records_updated = stats['records_updated']
            log_entry.success = True
            log_entry.save()
            
            return {
                'success': True,
                'message': f"تجمیع هفتگی با موفقیت انجام شد. {stats['records_created']} رکورد جدید، {stats['records_updated']} رکورد بروزرسانی شد.",
                'stats': stats
            }
            
        except Exception as e:
            error_msg = f"خطا در تجمیع داده‌های هفتگی: {str(e)}"
            self.logger.error(error_msg)
            
            log_entry.end_time = timezone.now()
            log_entry.error_message = error_msg
            log_entry.success = False
            log_entry.save()
            
            return {
                'success': False,
                'error': error_msg,
                'stats': stats
            }

    def aggregate_monthly_data(self) -> dict:
        """تجمیع داده‌های ماهانه"""
        # مشابه weekly اما گروه‌بندی براساس ماه
        # برای اختصار کد، الگوی مشابه را دنبال می‌کنیم
        pass

    def aggregate_yearly_data(self) -> dict:
        """تجمیع داده‌های سالانه"""
        # مشابه weekly اما گروه‌بندی براساس سال
        pass

    def run_all_aggregations(self) -> dict:
        """اجرای تمام عملیات تجمیع"""
        results = {}
        
        results['daily'] = self.aggregate_daily_data()
        results['weekly'] = self.aggregate_weekly_data() 
        # results['monthly'] = self.aggregate_monthly_data()
        # results['yearly'] = self.aggregate_yearly_data()
        
        return results
