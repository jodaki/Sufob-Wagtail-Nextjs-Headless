from django.core.management.base import BaseCommand
from wagtail.models import Page
from prices.models import PriceIndexPage, PricePage

class Command(BaseCommand):
    help = 'ایجاد صفحات قیمت برای Wagtail Admin'

    def handle(self, *args, **options):
        # پیدا کردن صفحه والد
        home_page = Page.objects.filter(depth=2).first()
        if not home_page:
            self.stdout.write(self.style.ERROR('صفحه والد پیدا نشد!'))
            return

        self.stdout.write(f'صفحه والد: {home_page.title}')

        # حذف صفحات موجود
        existing_prices = Page.objects.filter(slug='prices').first()
        if existing_prices:
            self.stdout.write('حذف صفحه قیمت‌های موجود...')
            existing_prices.delete()

        # ایجاد صفحه اصلی قیمت‌ها
        try:
            price_index = PriceIndexPage(
                title='قیمت کالاها',
                slug='prices', 
                intro='مشاهده نمودارهای قیمت کالاهای مختلف',
                show_in_menus=True,
                live=True
            )
            home_page.add_child(instance=price_index)
            price_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f'✓ صفحه اصلی ایجاد شد: {price_index.url}'))

            # ایجاد صفحات کالاها
            commodities = [
                ('قیمت طلا', 'طلا', 'gold'),
                ('قیمت نقره', 'نقره', 'silver'),
                ('قیمت مس', 'مس', 'copper')
            ]

            for title, commodity_name, slug in commodities:
                price_page = PricePage(
                    title=title,
                    commodity_name=commodity_name,
                    slug=slug,
                    intro=f'نمودار قیمت {commodity_name}',
                    show_in_menus=True,
                    live=True
                )
                price_index.add_child(instance=price_page)
                price_page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f'✓ {title}: {price_page.url}'))

            self.stdout.write(self.style.SUCCESS('\n🎉 همه صفحات ایجاد شدند!'))
            self.stdout.write('حالا از Wagtail Admin مدیریت کنید:')
            self.stdout.write('http://localhost:9000/sufobadmin/')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطا: {str(e)}'))
