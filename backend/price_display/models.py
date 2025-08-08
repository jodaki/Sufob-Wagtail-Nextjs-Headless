from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail_headless_preview.models import HeadlessPreviewMixin


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
    COMMODITY_CHOICES = [
        ('کنسانتره آهن', 'کنسانتره آهن'),
        ('سنگ آهن', 'سنگ آهن'),
        ('کاتد مس', 'کاتد مس'),
        ('شمش آلومینیوم', 'شمش آلومینیوم'),
        ('کک متالورژی', 'کک متالورژی'),
    ]
    
    commodity_name = models.CharField(
        max_length=100, 
        choices=COMMODITY_CHOICES,
        help_text="نام کالا را انتخاب کنید"
    )
    chart_description = RichTextField(blank=True, help_text="توضیحات چارت")
    show_statistics = models.BooleanField(default=True, help_text="نمایش آمار")
    chart_days = models.IntegerField(default=30, help_text="تعداد روزهای نمایش در چارت")
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('commodity_name'),
            FieldPanel('chart_days'),
            FieldPanel('show_statistics'),
        ], heading="تنظیمات چارت"),
        FieldPanel('chart_description'),
    ]
    
    # API fields for Next.js frontend
    api_fields = [
        APIField('commodity_name'),
        APIField('chart_description'),
        APIField('show_statistics'),
        APIField('chart_days'),
        APIField('get_chart_data'),
        APIField('get_statistics'),
    ]
    
    parent_page_types = ['price_display.PriceIndexPage']
    
    class Meta:
        verbose_name = "صفحه قیمت"
        verbose_name_plural = "صفحات قیمت"
        
    def __str__(self):
        return f"قیمت {self.commodity_name}"
    
    def get_chart_data(self):
        """دریافت داده‌های چارت از data_management"""
        from data_management.models import DailyData
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=self.chart_days)
        
        # دریافت داده‌های روزانه
        daily_data = DailyData.objects.filter(
            trade_date__range=[start_date, end_date]
        ).order_by('trade_date')
        
        # فرمت داده‌ها برای چارت
        chart_data = {
            'labels': [],
            'datasets': [{
                'label': f'قیمت {self.commodity_name}',
                'data': [],
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'tension': 0.1
            }]
        }
        
        for data in daily_data:
            chart_data['labels'].append(data.trade_date_shamsi or data.trade_date.strftime('%Y/%m/%d'))
            chart_data['datasets'][0]['data'].append(float(data.avg_final_price or 0))
        
        return chart_data
    
    def get_statistics(self):
        """دریافت آمار کلی"""
        from data_management.models import DailyData, AllData
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=self.chart_days)
        
        # آمار روزانه
        daily_stats = DailyData.objects.filter(
            trade_date__range=[start_date, end_date]
        ).aggregate(
            avg_price=models.Avg('avg_final_price'),
            max_price=models.Max('max_price'),
            min_price=models.Min('min_price'),
            total_volume=models.Sum('total_contracts_volume')
        )
        
        # آمار کلی از AllData
        all_data_stats = AllData.objects.filter(
            commodity_name=self.commodity_name
        ).aggregate(
            total_records=models.Count('id'),
            latest_date=models.Max('transaction_date')
        )
        
        return {
            'period_days': self.chart_days,
            'daily_stats': daily_stats,
            'all_data_stats': all_data_stats,
            'start_date': start_date.strftime('%Y/%m/%d'),
            'end_date': end_date.strftime('%Y/%m/%d')
        }
