from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail_headless_preview.models import HeadlessPreviewMixin
import jdatetime

# وابستگی‌ها
from price_data_ingestion.models import MainCategory, Category, SubCategory
from blog.models import BlogCategory, BlogPage
from data_management.models import AllData


class PriceIndexPage(HeadlessPreviewMixin, Page):
    """صفحه index برای قیمت‌ها - Headless CMS"""
    intro = RichTextField(blank=True, help_text="مقدمه صفحه قیمت‌ها")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    # API fields for Next.js frontend
    api_fields = [
        APIField('intro'),
    ]
    
    # تعیین کنید که چه نوع صفحه‌هایی می‌توانند فرزند این صفحه باشند
    subpage_types = ['price_display.PricePage']
    
    class Meta:
        verbose_name = "صفحه قیمت‌ها"
        verbose_name_plural = "صفحات قیمت‌ها"


class PricePage(HeadlessPreviewMixin, Page):
    """صفحه نمایش چارت قیمت برای یک کالا - Headless CMS"""

    # انتخاب دسته‌بندی کالا برای چارت
    main_category = models.ForeignKey(
        MainCategory,
        on_delete=models.PROTECT,
        related_name="price_pages",
        verbose_name="گروه اصلی",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="price_pages",
        verbose_name="گروه",
        null=True,
        blank=True,
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.PROTECT,
        related_name="price_pages",
        verbose_name="زیرگروه",
        null=True,
        blank=True,
    )

    chart_description = RichTextField(blank=True, help_text="توضیحات چارت")
    chart_days = models.IntegerField(default=30, help_text="تعداد روزهای نمایش در چارت")

    # فهرست مطالب (آخرین ۳ پست از یک دسته‌بندی وبلاگ)
    blog_category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name="فهرست مطالب",
        help_text="دسته‌بندی وبلاگ برای نمایش ۳ پست آخر",
    )
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('main_category'),
            FieldPanel('category'),
            FieldPanel('subcategory'),
            FieldPanel('chart_days'),
        ], heading="تنظیمات چارت"),
        FieldPanel('chart_description'),
        MultiFieldPanel([
            FieldPanel('blog_category'),
        ], heading="فهرست مطالب"),
    ]
    
    # API fields for Next.js frontend
    api_fields = [
        APIField('main_category'),
        APIField('category'),
        APIField('subcategory'),
        APIField('get_main_category_name'),
        APIField('get_category_name'),
        APIField('get_subcategory_name'),
        APIField('chart_description'),
        APIField('chart_days'),
        APIField('get_daily_chart_data'),
        APIField('get_weekly_chart_data'),
        APIField('get_monthly_chart_data'),
        APIField('get_yearly_chart_data'),
        APIField('get_latest_posts'),
    ]
    
    parent_page_types = ['price_display.PriceIndexPage']
    
    class Meta:
        verbose_name = "صفحه قیمت"
        verbose_name_plural = "صفحات قیمت"
        
    def __str__(self):
        return f"قیمت: {self.main_category.name} / {self.category.name} / {self.subcategory.name}"
    
    def _filtered_alldata_queryset(self):
        """برگرداندن کوئری داده‌های خام برای محصول انتخاب‌شده.
        سعی می‌کنیم بر اساس نام زیرگروه/گروه فیلتر کنیم (نزدیک‌ترین معیار موجود).
        """
        # تلاش برای فیلتر بر پایه نام کالا شامل نام زیرگروه یا گروه
        sub_name = self.subcategory.name if self.subcategory else ''
        cat_name = self.category.name if self.category else ''
        qs = AllData.objects.all()
        if sub_name:
            qs = qs.filter(commodity_name__icontains=sub_name)
        elif cat_name:
            qs = qs.filter(commodity_name__icontains=cat_name)
        return qs

    def get_daily_chart_data(self):
        """چارت روزانه از AllData برای محصول انتخاب‌شده (آخرین chart_days روز)."""
        # داده‌ها بر اساس تاریخ شمسی ذخیره شده‌اند به صورت YYYY/MM/DD
        qs = self._filtered_alldata_queryset()
        # آخرین chart_days روز بر اساس رشته تاریخ مرتب شده
        day_points = {}
        for item in qs.values('transaction_date', 'final_price'):
            d = item['transaction_date'] or ''
            try:
                price = float(item['final_price']) if item['final_price'] is not None else None
            except Exception:
                price = None
            if not d:
                continue
            lst = day_points.setdefault(d, [])
            if price is not None:
                lst.append(price)

        # محاسبه میانگین روزانه و مرتب‌سازی
        days_sorted = sorted(day_points.keys())[-self.chart_days:]
        labels = []
        data = []
        for d in days_sorted:
            prices = day_points[d]
            avg = sum(prices) / len(prices) if prices else 0
            labels.append(d)
            data.append(round(avg, 2))

        return {
            'labels': labels,
            'datasets': [{
                'label': f'قیمت {self.subcategory.name}',
                'data': data,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }]
        }

    def get_weekly_chart_data(self):
        """چارت هفتگی با تبدیل تاریخ شمسی به میلادی و گروه‌بندی هفته‌ای."""
        qs = self._filtered_alldata_queryset()
        week_points = {}
        for item in qs.values('transaction_date', 'final_price'):
            d = item['transaction_date'] or ''
            if not d or len(d) < 10:
                continue
            try:
                jy, jm, jd = int(d[0:4]), int(d[5:7]), int(d[8:10])
                gdate = jdatetime.date(jy, jm, jd).togregorian()
                year, week, _ = gdate.isocalendar()
                key = f"{year}-W{week:02d}"
                price = float(item['final_price']) if item['final_price'] is not None else None
            except Exception:
                continue
            lst = week_points.setdefault(key, [])
            if price is not None:
                lst.append(price)

        weeks_sorted = sorted(week_points.keys())
        labels = []
        data = []
        for key in weeks_sorted:
            prices = week_points[key]
            avg = sum(prices) / len(prices) if prices else 0
            labels.append(key)
            data.append(round(avg, 2))

        return {
            'labels': labels,
            'datasets': [{
                'label': f'میانگین هفتگی {self.subcategory.name}',
                'data': data,
                'borderColor': 'rgb(153, 102, 255)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                'tension': 0.1
            }]
        }

    def get_monthly_chart_data(self):
        """چارت ماهانه با گروه‌بندی بر اساس YYYY/MM از تاریخ شمسی."""
        qs = self._filtered_alldata_queryset()
        month_points = {}
        for item in qs.values('transaction_date', 'final_price'):
            d = item['transaction_date'] or ''
            if not d or len(d) < 7:
                continue
            key = d[0:7]  # YYYY/MM
            try:
                price = float(item['final_price']) if item['final_price'] is not None else None
            except Exception:
                price = None
            lst = month_points.setdefault(key, [])
            if price is not None:
                lst.append(price)

        months_sorted = sorted(month_points.keys())
        labels = []
        data = []
        for key in months_sorted:
            prices = month_points[key]
            avg = sum(prices) / len(prices) if prices else 0
            labels.append(key)
            data.append(round(avg, 2))

        return {
            'labels': labels,
            'datasets': [{
                'label': f'میانگین ماهانه {self.subcategory.name}',
                'data': data,
                'borderColor': 'rgb(255, 159, 64)',
                'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                'tension': 0.1
            }]
        }

    def get_yearly_chart_data(self):
        """چارت سالانه با گروه‌بندی بر اساس YYYY از تاریخ شمسی."""
        qs = self._filtered_alldata_queryset()
        year_points = {}
        for item in qs.values('transaction_date', 'final_price'):
            d = item['transaction_date'] or ''
            if not d or len(d) < 4:
                continue
            key = d[0:4]  # YYYY
            try:
                price = float(item['final_price']) if item['final_price'] is not None else None
            except Exception:
                price = None
            lst = year_points.setdefault(key, [])
            if price is not None:
                lst.append(price)

        years_sorted = sorted(year_points.keys())
        labels = []
        data = []
        for key in years_sorted:
            prices = year_points[key]
            avg = sum(prices) / len(prices) if prices else 0
            labels.append(key)
            data.append(round(avg, 2))

        return {
            'labels': labels,
            'datasets': [{
                'label': f'میانگین سالانه {self.subcategory.name}',
                'data': data,
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'tension': 0.1
            }]
        }
    
    def get_latest_posts(self):
        """آخرین سه پست وبلاگ از دسته‌بندی انتخاب‌شده."""
        if not self.blog_category:
            return []
        # انتخاب آخرین ۳ پست دارای این دسته‌بندی
        posts = (
            BlogPage.objects.live()
            .filter(categories=self.blog_category)
            .order_by('-first_published_at')[:3]
        )
        # بازگرداندن داده‌های ساده برای API
        return [
            {
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'first_published_at': p.first_published_at,
                'url': p.url,
            }
            for p in posts
        ]

    def get_main_category_name(self):
        """بازگرداندن نام گروه اصلی برای API"""
        return self.main_category.name if self.main_category else None

    def get_category_name(self):
        """بازگرداندن نام گروه برای API"""
        return self.category.name if self.category else None

    def get_subcategory_name(self):
        """بازگرداندن نام زیرگروه برای API"""
        return self.subcategory.name if self.subcategory else None

    # اعتبارسنجی ارتباطات انتخابی
    def clean(self):
        super().clean()
        errors = {}
        if self.category and self.main_category and self.category.main_category_id != self.main_category_id:
            errors['category'] = "گروه انتخاب‌شده با گروه اصلی هماهنگ نیست."
        if self.subcategory and self.category and self.subcategory.category_id != self.category_id:
            errors['subcategory'] = "زیرگروه انتخاب‌شده با گروه هماهنگ نیست."
        if errors:
            from django.core.exceptions import ValidationError
            raise ValidationError(errors)
