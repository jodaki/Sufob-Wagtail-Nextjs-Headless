from django.core.management.base import BaseCommand
from prices.models import ScrollTimeRequest, MainCategory, Category, SubCategory
from prices.services import ScrollTimeService
import json

class Command(BaseCommand):
    help = 'Test Scroll Time API with different scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--main-cat',
            type=int,
            help='Main category value (default: 2 for صنعتی)',
            default=2
        )
        parser.add_argument(
            '--cat',
            type=int,
            help='Category value (default: 49 for سنگ آهن)',
            default=49
        )
        parser.add_argument(
            '--subcat',
            type=int,
            help='SubCategory value (default: 464 for گندله)',
            default=464
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 شروع تست API سازمان بورس...'))
        
        try:
            # Find categories by value
            main_cat = MainCategory.objects.get(value=options['main_cat'])
            cat = Category.objects.get(value=options['cat'])
            subcat = SubCategory.objects.get(value=options['subcat'])
            
            self.stdout.write(f'📂 Categories: {main_cat.name} -> {cat.name} -> {subcat.name}')
            
            # Create test request
            request = ScrollTimeRequest.objects.create(
                main_category=main_cat,
                category=cat,
                subcategory=subcat,
                start_date_shamsi='1403/05/01',
                end_date_shamsi='1403/05/05',
                created_by='API Test Command'
            )
            
            # Get payload
            payload = request.get_payload()
            self.stdout.write('\n📝 Payload ارسالی:')
            for key, value in payload.items():
                self.stdout.write(f'   {key}: {value}')
            
            # Initialize service and show headers
            service = ScrollTimeService()
            self.stdout.write('\n📡 Headers ارسالی:')
            for key, value in service.DEFAULT_HEADERS.items():
                self.stdout.write(f'   {key}: {value}')
                
            self.stdout.write(f'\n🔗 URL: {service.BASE_URL}')
            
            # Test API call
            self.stdout.write('\n⏳ در حال ارسال درخواست...')
            result = service.fetch_data(request)
            
            self.stdout.write('\n📊 نتیجه:')
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'✅ موفق: {result["total_records"]} رکورد دریافت شد'))
                self.stdout.write(result['message'])
            else:
                self.stdout.write(self.style.ERROR(f'❌ خطا: {result["error"]}'))
                
                if 'debug_details' in result:
                    self.stdout.write('\n🔧 جزئیات debug:')
                    debug_details = result['debug_details']
                    for key, value in debug_details.items():
                        if key == 'response_text' and len(str(value)) > 200:
                            self.stdout.write(f'   {key}: {str(value)[:200]}...')
                        else:
                            self.stdout.write(f'   {key}: {value}')
            
            # Request status
            request.refresh_from_db()
            self.stdout.write(f'\n📈 وضعیت درخواست: {request.status}')
            if request.error_message:
                self.stdout.write(f'💬 پیام خطا: {request.error_message[:200]}...')
                
        except MainCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ MainCategory با value {options["main_cat"]} پیدا نشد'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Category با value {options["cat"]} پیدا نشد'))
        except SubCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ SubCategory با value {options["subcat"]} پیدا نشد'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ خطای غیرمنتظره: {str(e)}'))
            import traceback
            traceback.print_exc()
        
        self.stdout.write(self.style.SUCCESS('\n🏁 تست تمام شد.'))
