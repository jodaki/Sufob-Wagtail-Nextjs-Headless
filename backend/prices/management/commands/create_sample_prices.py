from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page, Site
from home.models import HomePage
from prices.models import PriceIndexPage, PricePage

class Command(BaseCommand):
    help = 'ایجاد صفحات نمونه برای سیستم قیمت‌گذاری'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='حذف صفحات موجود و ایجاد مجدد',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # پیدا کردن صفحه اصلی
        try:
            home_page = HomePage.objects.first()
            if not home_page:
                self.stdout.write(self.style.ERROR('صفحه اصلی پیدا نشد!'))
                return
        except:
            # اگر HomePage نیست، از Root Page استفاده کن
            home_page = Page.objects.filter(depth=2).first()
            if not home_page:
                self.stdout.write(self.style.ERROR('صفحه والد مناسب پیدا نشد!'))
                return

        # بررسی وجود صفحه قیمت‌ها
        existing_price_index = PriceIndexPage.objects.filter(
            slug='prices'
        ).first()

        if existing_price_index and force:
            self.stdout.write('حذف صفحات موجود...')
            existing_price_index.delete()
            existing_price_index = None

        if not existing_price_index:
            # ایجاد صفحه اصلی قیمت‌ها
            price_index_page = PriceIndexPage(
                title='قیمت کالاها',
                slug='prices',
                intro='مشاهده نمودارهای قیمت کالاهای مختلف بورس کالا',
                show_in_menus=True,
                live=True
            )
            home_page.add_child(instance=price_index_page)
            price_index_page.save_revision().publish()
            self.stdout.write(
                self.style.SUCCESS(f'✓ صفحه اصلی قیمت‌ها ایجاد شد: {price_index_page.url}')
            )
        else:
            price_index_page = existing_price_index
            self.stdout.write('صفحه اصلی قیمت‌ها قبلاً وجود دارد.')

        # لیست کالاهای نمونه برای ایجاد صفحه
        sample_commodities = [
            {
                'title': 'قیمت طلا',
                'commodity_name': 'طلا',
                'slug': 'gold',
                'intro': 'مشاهده نمودار قیمت طلا و تحلیل روند قیمتی'
            },
            {
                'title': 'قیمت نقره',
                'commodity_name': 'نقره', 
                'slug': 'silver',
                'intro': 'پیگیری قیمت نقره و تغییرات بازار'
            },
            {
                'title': 'قیمت مس',
                'commodity_name': 'مس',
                'slug': 'copper',
                'intro': 'بررسی روند قیمت مس در بورس کالا'
            },
            {
                'title': 'قیمت آلومینیوم',
                'commodity_name': 'آلومینیوم',
                'slug': 'aluminum',
                'intro': 'تحلیل قیمت آلومینیوم و پیش‌بینی روند'
            },
            {
                'title': 'قیمت روی',
                'commodity_name': 'روی',
                'slug': 'zinc',
                'intro': 'مشاهده نمودار قیمت روی و آمار معاملات'
            }
        ]

        # ایجاد صفحات کالاها
        created_count = 0
        for commodity in sample_commodities:
            existing_page = PricePage.objects.filter(
                parent=price_index_page,
                slug=commodity['slug']
            ).first()

            if existing_page and force:
                existing_page.delete()
                existing_page = None

            if not existing_page:
                price_page = PricePage(
                    title=commodity['title'],
                    commodity_name=commodity['commodity_name'],
                    slug=commodity['slug'],
                    intro=commodity['intro'],
                    show_in_menus=True,
                    live=True
                )
                price_index_page.add_child(instance=price_page)
                price_page.save_revision().publish()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ صفحه {commodity["title"]} ایجاد شد: {price_page.url}')
                )
            else:
                self.stdout.write(f'صفحه {commodity["title"]} قبلاً وجود دارد.')

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 کار تمام شد! {created_count} صفحه جدید ایجاد شد.')
        )
        self.stdout.write(
            f'🔗 لینک صفحه اصلی: {price_index_page.full_url}'
        )
        self.stdout.write(
            '💡 حالا می‌توانید از طریق Wagtail Admin این صفحات را مدیریت کنید.'
        )
