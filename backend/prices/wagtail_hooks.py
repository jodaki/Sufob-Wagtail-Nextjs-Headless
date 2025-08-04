from django.urls import path, reverse, include
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register, ModelAdminGroup
)
from .models import PricePage, PriceIndexPage, PriceData, DataImportLog
from .forms import DataImportForm


# ModelAdmin classes for Wagtail admin
class PriceDataAdmin(ModelAdmin):
    model = PriceData
    menu_label = 'داده‌های قیمت'
    menu_icon = 'table'
    menu_order = 310
    list_display = ('commodity_name', 'price_date', 'final_price', 'avg_price', 'volume', 'created_at')
    list_filter = ('commodity_name', 'price_date', 'source', 'created_at')
    search_fields = ('commodity_name', 'symbol')
    inspect_view_enabled = True
    inspect_view_fields = ('commodity_name', 'symbol', 'price_date', 'final_price', 'avg_price', 
                           'lowest_price', 'highest_price', 'volume', 'value', 'unit', 
                           'created_at', 'updated_at', 'source')


class DataImportLogAdmin(ModelAdmin):
    model = DataImportLog
    menu_label = 'لاگ‌های وارد کردن داده'
    menu_icon = 'history'
    menu_order = 330
    list_display = ('commodity_name', 'start_date', 'end_date', 'total_records', 
                    'imported_records', 'status', 'created_at', 'created_by')
    list_filter = ('status', 'commodity_name', 'created_at')
    search_fields = ('commodity_name', 'created_by')
    inspect_view_enabled = True
    inspect_view_fields = ('commodity_name', 'start_date', 'end_date', 'total_records', 
                           'imported_records', 'updated_records', 'duplicate_records', 
                           'error_records', 'status', 'error_message', 'created_at', 'created_by')


# Custom import view
class PriceDataImportAdmin(ModelAdmin):
    model = PriceData
    menu_label = '🔄 وارد کردن داده‌های قیمت'
    menu_icon = 'download'
    menu_order = 320
    
    def get_admin_urls_for_registration(self):
        """Override to add custom URL for import view"""
        from django.urls import path
        urls = super().get_admin_urls_for_registration()
        urls = urls + (
            path('import/', self.import_view, name=self.url_helper.get_action_url_name('import')),
        )
        return urls
    
    def import_view(self, request):
        """Custom view for importing price data"""
        if request.method == 'POST':
            form = DataImportForm(request.POST)
            if form.is_valid():
                # Process form data
                result = self.process_import(form.cleaned_data, request.user)
                messages.success(request, f'عملیات با موفقیت انجام شد. {result["imported"]} رکورد وارد شد.')
                return HttpResponseRedirect(request.path)
        else:
            form = DataImportForm()
        
        # Statistics
        from django.db import models
        stats = {
            'total_records': PriceData.objects.count(),
            'commodities_count': PriceData.objects.values('commodity_name').distinct().count(),
            'latest_date': PriceData.objects.aggregate(models.Max('price_date'))['price_date__max'],
            'recent_imports': DataImportLog.objects.order_by('-created_at')[:5]
        }
        
        # Render the template
        from django.template.response import TemplateResponse
        return TemplateResponse(request, 'prices/price_data_import.html', {
            'form': form,
            'stats': stats,
            'title': 'وارد کردن داده‌های قیمت',
            'self': self,
        })
    
    def process_import(self, data, user):
        """Process data import"""
        # Implementation of data import logic would go here
        # This is a placeholder
        return {
            'imported': 0,
            'updated': 0,
            'duplicates': 0,
            'errors': 0
        }


# Group all the price-related admin views
class PricesAdminGroup(ModelAdminGroup):
    menu_label = 'مدیریت قیمت‌ها'
    menu_icon = 'doc-full'
    menu_order = 300
    items = (PriceDataAdmin, PriceDataImportAdmin, DataImportLogAdmin)


# Register the admin group with Wagtail
modeladmin_register(PricesAdminGroup)

# برای نمایش بهتر در لیست صفحات
@hooks.register('construct_page_listing_buttons')
def page_listing_buttons(buttons, page, page_perms, is_parent=False):
    if isinstance(page, (PricePage, PriceIndexPage)):
        buttons.append(
            format_html(
                '<a href="/admin/pages/{}/edit/" class="button button-small button-secondary">ویرایش قیمت</a>',
                page.id
            )
        )
    return buttons

# اضافه کردن اطلاعات بیشتر در لیست صفحات
@hooks.register('construct_page_chooser_queryset')
def show_price_pages_in_chooser(pages, request):
    # نمایش صفحات قیمت در page chooser
    return pages

# کمک برای مدیران در درک صفحات قیمت
@hooks.register('before_edit_page')
def before_edit_price_page(request, page):
    if isinstance(page, PricePage):
        from django.contrib import messages
        messages.info(
            request, 
            f'این یک صفحه قیمت برای کالای "{page.commodity_name}" است. '
            'تغییرات شما در API قابل دسترس خواهد بود.'
        )

@hooks.register('before_edit_page')
def before_edit_price_index_page(request, page):
    if isinstance(page, PriceIndexPage):
        from django.contrib import messages
        messages.info(
            request, 
            'این صفحه اصلی تمام قیمت‌هاست. صفحات فرزند آن شامل قیمت‌های مختلف کالاها می‌شود.'
        )
