from django.core.management.base import BaseCommand
from data_management.models import AllData
from data_management.signals import aggregate_daily_data, aggregate_weekly_data, aggregate_monthly_data, aggregate_yearly_data, shamsi_to_gregorian
from collections import defaultdict


class Command(BaseCommand):
    help = 'تجمیع تمام داده‌های تاریخی'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='بازتولید داده‌های تجمیعی حتی اگر قبلاً وجود داشته باشند',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # گروه‌بندی داده‌ها بر اساس تاریخ میلادی
        dates_to_aggregate = set()
        all_records = AllData.objects.all()
        
        self.stdout.write(f'تعداد کل رکوردها: {all_records.count()}')
        
        for record in all_records:
            if record.transaction_date:
                # تبدیل تاریخ شمسی به میلادی
                gregorian_date = shamsi_to_gregorian(record.transaction_date)
                if gregorian_date:
                    dates_to_aggregate.add(gregorian_date)
        
        self.stdout.write(f'تعداد تاریخ‌های منحصر به فرد: {len(dates_to_aggregate)}')
        
        # تجمیع برای هر تاریخ
        processed = 0
        for date in sorted(dates_to_aggregate):
            self.stdout.write(f'تجمیع برای تاریخ: {date}')
            
            # تجمیع روزانه
            aggregate_daily_data(date, force=force)
            
            # تجمیع هفتگی، ماهانه و سالانه
            aggregate_weekly_data(date, force=force)
            aggregate_monthly_data(date, force=force)
            aggregate_yearly_data(date, force=force)
            
            processed += 1
            
            if processed % 10 == 0:
                self.stdout.write(f'پردازش شد: {processed}/{len(dates_to_aggregate)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'تجمیع کامل شد! {processed} تاریخ پردازش شد.')
        )
