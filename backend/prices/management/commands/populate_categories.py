"""
Django management command برای پرکردن داده‌های اولیه دسته‌بندی‌ها
"""
from django.core.management.base import BaseCommand
from prices.models import MainCategory, Category, SubCategory


class Command(BaseCommand):
    help = 'پرکردن داده‌های اولیه دسته‌بندی‌ها برای Scroll Time'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('شروع پرکردن داده‌های اولیه...'))
        
        # ایجاد گروه‌های اصلی
        main_categories_data = [
            {'value': 0, 'name': '[همه گروه های اصلی]', 'order': 0},
            {'value': 1, 'name': 'صنعتی', 'order': 1},
            {'value': 2, 'name': 'کشاورزی', 'order': 2},
            {'value': 3, 'name': 'پتروشیمی و فرآورده های نفتی', 'order': 3},
            {'value': 4, 'name': 'معدنی', 'order': 4},
            {'value': 5, 'name': 'فرآورده های نفتی', 'order': 5},
            {'value': 6, 'name': 'اموال غیر منقول', 'order': 6},
        ]
        
        main_categories = {}
        for data in main_categories_data:
            main_cat, created = MainCategory.objects.get_or_create(
                value=data['value'],
                defaults={
                    'name': data['name'],
                    'order': data['order'],
                    'is_active': True
                }
            )
            main_categories[data['value']] = main_cat
            if created:
                self.stdout.write(f'✓ ایجاد گروه اصلی: {main_cat.name}')
            else:
                self.stdout.write(f'- گروه اصلی موجود: {main_cat.name}')
        
        # ایجاد گروه‌ها
        categories_data = [
            {'value': 0, 'name': '[همه گروه ها]', 'main_cat': 0, 'order': 0},
            {'value': 1, 'name': 'فولاد', 'main_cat': 1, 'order': 1},
            {'value': 2, 'name': 'آلومینیوم', 'main_cat': 1, 'order': 2},
            {'value': 3, 'name': 'مس', 'main_cat': 1, 'order': 3},
            {'value': 4, 'name': 'روی', 'main_cat': 1, 'order': 4},
            {'value': 5, 'name': 'کنسانتره', 'main_cat': 1, 'order': 5},
            {'value': 6, 'name': 'کنسانتره مولیبدن', 'main_cat': 1, 'order': 6},
            {'value': 20, 'name': 'طلا', 'main_cat': 4, 'order': 20},
            {'value': 38, 'name': 'نیکل', 'main_cat': 1, 'order': 38},
            {'value': 40, 'name': 'کک', 'main_cat': 1, 'order': 40},
            {'value': 41, 'name': 'سیمان', 'main_cat': 1, 'order': 41},
            {'value': 49, 'name': 'سنگ آهن', 'main_cat': 1, 'order': 49},
            {'value': 90, 'name': 'سرب', 'main_cat': 1, 'order': 90},
            {'value': 91, 'name': 'خودرو', 'main_cat': 1, 'order': 91},
            {'value': 97, 'name': 'آهن اسفنجی', 'main_cat': 1, 'order': 97},
        ]
        
        categories = {}
        for data in categories_data:
            if data['main_cat'] in main_categories:
                cat, created = Category.objects.get_or_create(
                    value=data['value'],
                    main_category=main_categories[data['main_cat']],
                    defaults={
                        'name': data['name'],
                        'order': data['order'],
                        'is_active': True
                    }
                )
                categories[data['value']] = cat
                if created:
                    self.stdout.write(f'  ✓ ایجاد گروه: {cat.name} (زیر {cat.main_category.name})')
                else:
                    self.stdout.write(f'  - گروه موجود: {cat.name}')
        
        # ایجاد زیرگروه‌ها
        subcategories_data = [
            {'value': 0, 'name': '[همه زیرگروه‌ها]', 'cat': 49, 'order': 0},
            {'value': 198, 'name': 'سنگ آهن دانه‌بندی', 'cat': 49, 'order': 198},
            {'value': 464, 'name': 'گندله', 'cat': 49, 'order': 464},
            {'value': 477, 'name': 'کنسانتره', 'cat': 49, 'order': 477},
            {'value': 489, 'name': 'سنگ آهن کلوخه', 'cat': 49, 'order': 489},
        ]
        
        for data in subcategories_data:
            if data['cat'] in categories:
                subcat, created = SubCategory.objects.get_or_create(
                    value=data['value'],
                    category=categories[data['cat']],
                    defaults={
                        'name': data['name'],
                        'order': data['order'],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'    ✓ ایجاد زیرگروه: {subcat.name} (زیر {subcat.category.name})')
                else:
                    self.stdout.write(f'    - زیرگروه موجود: {subcat.name}')
        
        self.stdout.write(self.style.SUCCESS('✅ پرکردن داده‌های اولیه با موفقیت تکمیل شد!'))
