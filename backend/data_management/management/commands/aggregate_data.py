from django.core.management.base import BaseCommand
from data_management.services import DataAggregationService


class Command(BaseCommand):
    help = 'تجمیع داده‌های مدیریت داده براساس بازه‌های زمانی مختلف'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['daily', 'weekly', 'monthly', 'yearly', 'all'],
            default='all',
            help='نوع تجمیع: daily, weekly, monthly, yearly, all'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='تاریخ شروع (فرمت: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='تاریخ پایان (فرمت: YYYY-MM-DD)'
        )

    def handle(self, *args, **options):
        service = DataAggregationService()
        aggregation_type = options['type']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 شروع تجمیع داده‌ها - نوع: {aggregation_type}')
        )
        
        try:
            if aggregation_type == 'daily' or aggregation_type == 'all':
                self.stdout.write('📊 تجمیع داده‌های روزانه...')
                result = service.aggregate_daily_data()
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {result["message"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {result["error"]}')
                    )
            
            if aggregation_type == 'weekly' or aggregation_type == 'all':
                self.stdout.write('📈 تجمیع داده‌های هفتگی...')
                result = service.aggregate_weekly_data()
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {result["message"]}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ {result["error"]}')
                    )
            
            # سایر انواع تجمیع را می‌توان اضافه کرد
            
            self.stdout.write(
                self.style.SUCCESS('🎉 عملیات تجمیع داده‌ها با موفقیت تکمیل شد!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'💥 خطای کلی در تجمیع داده‌ها: {str(e)}')
            )
