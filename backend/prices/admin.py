from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Count, Avg, Max, Min
from .models import PriceIndexPage, PricePage, PriceData, DataImportLog
from .forms import DataImportForm
import json

@admin.register(PricePage)
class PricePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'commodity_name', 'slug', 'live', 'first_published_at')
    list_filter = ('live', 'first_published_at', 'commodity_name')
    search_fields = ('title', 'commodity_name', 'slug')
    readonly_fields = ('slug', 'path', 'depth', 'numchild', 'url_path')
    
    fieldsets = (
        ('اطلاعات صفحه قیمت', {
            'fields': ('title', 'commodity_name', 'chart_description')
        }),
        ('تنظیمات چارت', {
            'fields': ('show_statistics', 'chart_days')
        }),
        ('تنظیمات انتشار', {
            'fields': ('slug', 'live', 'show_in_menus')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('path', 'depth', 'numchild', 'url_path'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PriceIndexPage)
class PriceIndexPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'live', 'first_published_at')
    list_filter = ('live', 'first_published_at')
    search_fields = ('title', 'slug')
    readonly_fields = ('slug', 'path', 'depth', 'numchild', 'url_path')
    
    fieldsets = (
        ('اطلاعات صفحه اصلی قیمت‌ها', {
            'fields': ('title', 'intro')
        }),
        ('تنظیمات انتشار', {
            'fields': ('slug', 'live', 'show_in_menus')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('path', 'depth', 'numchild', 'url_path'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PriceData)
class PriceDataAdmin(admin.ModelAdmin):
    list_display = ('commodity_name', 'price_date', 'final_price', 'avg_price', 'volume', 'created_at')
    list_filter = ('commodity_name', 'price_date', 'source', 'created_at')
    search_fields = ('commodity_name', 'symbol')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'price_date'
    list_per_page = 50
    
    fieldsets = (
        ('اطلاعات کالا', {
            'fields': ('commodity_name', 'symbol', 'price_date')
        }),
        ('اطلاعات قیمت', {
            'fields': ('final_price', 'avg_price', 'lowest_price', 'highest_price')
        }),
        ('اطلاعات معاملات', {
            'fields': ('volume', 'value', 'unit')
        }),
        ('متاداده', {
            'fields': ('source', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_selected_data', 'bulk_delete_selected']
    
    def export_selected_data(self, request, queryset):
        """خروجی گرفتن از داده‌های انتخاب شده"""
        selected = queryset.values_list('id', flat=True)
        return HttpResponseRedirect(f'/admin/prices/export/?ids={",".join(map(str, selected))}')
    export_selected_data.short_description = "خروجی Excel از داده‌های انتخاب شده"
    
    def bulk_delete_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} رکورد حذف شد.', messages.SUCCESS)
    bulk_delete_selected.short_description = "حذف گروهی داده‌های انتخاب شده"

@admin.register(DataImportLog)
class DataImportLogAdmin(admin.ModelAdmin):
    list_display = ('commodity_name', 'start_date', 'end_date', 'total_records', 
                   'imported_records', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'commodity_name', 'created_at')
    search_fields = ('commodity_name', 'created_by')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('اطلاعات واردات', {
            'fields': ('commodity_name', 'start_date', 'end_date', 'created_by')
        }),
        ('نتایج واردات', {
            'fields': ('total_records', 'imported_records', 'updated_records', 
                      'duplicate_records', 'error_records', 'status')
        }),
        ('جزئیات خطا', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('زمان‌بندی', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # فقط خواندنی
    
    def has_change_permission(self, request, obj=None):
        return False  # فقط خواندنی


# کلاس‌های کمکی برای مدیریت داده‌ها
class PriceDataImportAdmin(admin.ModelAdmin):
    """کلاس مخصوص وارد کردن داده‌های قیمت"""
    change_list_template = 'admin/prices/price_data_import.html'
    
    def changelist_view(self, request, extra_context=None):
        """نمایش فرم وارد کردن داده"""
        extra_context = extra_context or {}
        
        if request.method == 'POST':
            form = DataImportForm(request.POST)
            if form.is_valid():
                # پردازش فرم و وارد کردن داده‌ها
                result = self.process_import(form.cleaned_data, request.user)
                messages.success(request, f'عملیات با موفقیت انجام شد. {result["imported"]} رکورد وارد شد.')
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = DataImportForm()
        
        # آمار کلی
        stats = {
            'total_records': PriceData.objects.count(),
            'commodities_count': PriceData.objects.values('commodity_name').distinct().count(),
            'latest_date': PriceData.objects.aggregate(Max('price_date'))['price_date__max'],
            'recent_imports': DataImportLog.objects.order_by('-created_at')[:5]
        }
        
        extra_context.update({
            'form': form,
            'stats': stats,
            'title': 'وارد کردن داده‌های قیمت',
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def process_import(self, data, user):
        """پردازش عملیات وارد کردن داده"""
        # این متد باید منطق وارد کردن داده را پیاده‌سازی کند
        # فعلاً یک پیاده‌سازی ساده
        return {
            'imported': 0,
            'updated': 0,
            'duplicates': 0,
            'errors': 0
        }
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

# ثبت کلاس مدیریت وارد کردن داده
class PriceDataImportProxy(PriceData):
    """کلاس Proxy برای مدیریت وارد کردن داده‌ها"""
    class Meta:
        proxy = True
        verbose_name = "وارد کردن داده قیمت"
        verbose_name_plural = "🔄 وارد کردن داده‌های قیمت"

admin.site.register(PriceDataImportProxy, PriceDataImportAdmin)
