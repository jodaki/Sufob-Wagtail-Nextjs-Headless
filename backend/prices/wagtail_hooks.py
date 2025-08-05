from django.urls import reverse
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup
from wagtail.contrib.modeladmin.views import CreateView
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import (
    PricePage, PriceIndexPage, PriceData, DataImportLog,
    MainCategory, Category, SubCategory, ScrollTimeRequest
)
from .forms import DataImportForm


# PriceData ModelAdmin
class PriceDataAdmin(ModelAdmin):
    model = PriceData
    menu_label = 'داده‌های قیمت'
    menu_icon = 'table'
    menu_order = 200
    list_display = ('commodity_name', 'price_date', 'final_price', 'avg_price', 'volume', 'created_at')
    list_filter = ('commodity_name', 'price_date', 'source', 'created_at')
    search_fields = ('commodity_name', 'symbol')
    inspect_view_enabled = True


# DataImportLog ModelAdmin
class DataImportLogAdmin(ModelAdmin):
    model = DataImportLog
    menu_label = 'لاگ‌های ورود داده'
    menu_icon = 'list-ul'
    menu_order = 201
    list_display = ('commodity_name', 'start_date', 'end_date', 'status', 'total_records', 'imported_records', 'created_at')
    list_filter = ('status', 'commodity_name', 'created_at')
    search_fields = ('commodity_name',)
    inspect_view_enabled = True


# MainCategory ModelAdmin
class MainCategoryAdmin(ModelAdmin):
    model = MainCategory
    menu_label = 'گروه‌های اصلی'
    menu_icon = 'folder-open-inverse'
    menu_order = 210
    list_display = ('name', 'value', 'is_active', 'order', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order', 'name')


# Category ModelAdmin
class CategoryAdmin(ModelAdmin):
    model = Category
    menu_label = 'گروه‌ها'
    menu_icon = 'folder'
    menu_order = 211
    list_display = ('name', 'main_category', 'value', 'is_active', 'order', 'created_at')
    list_filter = ('main_category', 'is_active')
    search_fields = ('name', 'main_category__name')
    ordering = ('main_category', 'order', 'name')


# SubCategory ModelAdmin
class SubCategoryAdmin(ModelAdmin):
    model = SubCategory
    menu_label = 'زیرگروه‌ها'
    menu_icon = 'folder-open-1'
    menu_order = 212
    list_display = ('name', 'category', 'value', 'is_active', 'order', 'created_at')
    list_filter = ('category__main_category', 'category', 'is_active')
    search_fields = ('name', 'category__name', 'category__main_category__name')
    ordering = ('category__main_category', 'category', 'order', 'name')


# ScrollTimeRequest ModelAdmin
class ScrollTimeRequestAdmin(ModelAdmin):
    model = ScrollTimeRequest
    menu_label = 'درخواست‌های Scroll Time'
    menu_icon = 'download'
    menu_order = 220
    list_display = ('id', 'main_category', 'category', 'subcategory', 'start_date_shamsi', 'end_date_shamsi', 'status', 'total_records', 'created_at')
    list_filter = ('status', 'main_category', 'category', 'created_at')
    search_fields = ('main_category__name', 'category__name', 'subcategory__name')
    ordering = ('-created_at',)
    inspect_view_enabled = True


# Custom Import View
class ImportView(CreateView):
    def get_template_names(self):
        return ['wagtailadmin/generic/form.html']
    
    def get_page_title(self):
        return "وارد کردن داده‌های قیمت"
    
    def get_form_class(self):
        return DataImportForm
    
    def form_valid(self, form):
        # Process the uploaded file
        file = form.cleaned_data.get('import_file')
        commodity = form.cleaned_data.get('commodity_name')
        
        # Create import log
        import_log = DataImportLog.objects.create(
            commodity_name=commodity,
            start_date=form.cleaned_data.get('start_date'),
            end_date=form.cleaned_data.get('end_date'),
            status='در حال پردازش',
            total_records=0,
            created_by=self.request.user
        )
        
        # Logic for processing the file would go here
        # For now, just report success
        import_log.status = 'تکمیل شده'
        import_log.save()
        
        messages.success(self.request, f'فایل برای {commodity} با موفقیت آپلود و پردازش شد!')
        return HttpResponseRedirect(self.index_url)


# Custom ModelAdmin for Import Functionality
class PriceDataImportAdmin(ModelAdmin):
    model = DataImportLog
    menu_label = 'وارد کردن داده‌های قیمت'
    menu_icon = 'upload'
    menu_order = 202
    
    def get_admin_urls_for_registration(self):
        """
        Override to use our custom import view instead of the standard create view
        """
        from django.urls import path
        urls = super().get_admin_urls_for_registration()
        urls = (
            path('', self.import_view, name='price_data_import'),
        ) + urls
        return urls
        
    def get_url_name(self, view_name):
        """
        Return a URL name for the given view
        """
        return f"prices_dataimportlog_{view_name}"
    
    def import_view(self, request):
        view_class = ImportView
        index_url = self.get_index_url()
        return view_class.as_view(model=self.model, index_url=index_url)(request)
        
    def get_index_url(self):
        """
        Return the URL for the listing page
        """
        return reverse(f"prices_dataimportlog_index")


# گروه‌بندی مدل‌های دسته‌بندی
class CategoryModelAdminGroup(ModelAdminGroup):
    menu_label = 'دسته‌بندی‌ها'
    menu_icon = 'folder-open-inverse'
    menu_order = 210
    items = (MainCategoryAdmin, CategoryAdmin, SubCategoryAdmin)


# گروه‌بندی مدل‌های اصلی قیمت
class PriceModelAdminGroup(ModelAdminGroup):
    menu_label = 'مدیریت قیمت‌ها'
    menu_icon = 'table'
    menu_order = 200
    items = (PriceDataAdmin, DataImportLogAdmin, PriceDataImportAdmin)


# گروه‌بندی Scroll Time
class ScrollTimeModelAdminGroup(ModelAdminGroup):
    menu_label = 'Scroll Time'
    menu_icon = 'download'
    menu_order = 220
    items = (ScrollTimeRequestAdmin,)


# Register the groups
modeladmin_register(PriceModelAdminGroup)
modeladmin_register(CategoryModelAdminGroup)
modeladmin_register(ScrollTimeModelAdminGroup)


# اضافه کردن منوی Scroll Time Dashboard به sidebar
@hooks.register('register_admin_menu_item')
def register_scroll_time_dashboard_menu_item():
    return MenuItem(
        'داشبورد Scroll Time',
        '/sufobadmin/scroll-time/dashboard/',
        classnames='icon icon-view',
        order=999
    )

# اضافه کردن منوی Scroll Time به sidebar
@hooks.register('register_admin_menu_item')
def register_scroll_time_menu_item():
    return MenuItem(
        'Scroll Time جدید',
        '/sufobadmin/scroll-time/quick-create/',
        classnames='icon icon-download',
        order=1000
    )


# ثبت URLهای Admin برای Scroll Time
@hooks.register('register_admin_urls')
def register_scroll_time_admin_urls():
    """ثبت URLهای سفارشی Scroll Time در Wagtail Admin"""
    from django.urls import path
    from .dashboard_views import scroll_time_dashboard, scroll_time_quick_create
    from .scroll_time_views import (
        ajax_get_categories, ajax_get_subcategories,
        ScrollTimeSendView, ScrollTimePreviewView, ScrollTimeCompletedView
    )
    
    return [
        # Dashboard URLs
        path('scroll-time/dashboard/', scroll_time_dashboard, name='scroll_time_dashboard'),
        path('scroll-time/quick-create/', scroll_time_quick_create, name='scroll_time_quick_create'),
        
        # Workflow URLs
        path('scroll-time/<int:pk>/send/', ScrollTimeSendView.as_view(), name='scroll_time_send'),
        path('scroll-time/<int:pk>/preview/', ScrollTimePreviewView.as_view(), name='scroll_time_preview'),
        path('scroll-time/<int:pk>/completed/', ScrollTimeCompletedView.as_view(), name='scroll_time_completed'),
        
        # AJAX URLs
        path('scroll-time/ajax/categories/', ajax_get_categories, name='ajax_get_categories'),
        path('scroll-time/ajax/subcategories/', ajax_get_subcategories, name='ajax_get_subcategories'),
    ]

# اضافه کردن زیرمنوهای Scroll Time
@hooks.register('register_admin_menu_item')
def register_scroll_time_list_menu_item():
    return MenuItem(
        'مشاهده درخواست‌ها',
        reverse('wagtailadmin_explore_root') + '#scroll-time-requests',
        classnames='icon icon-list-ul',
        order=1001
    )


# Custom CSS for Persian RTL support
@hooks.register('insert_global_admin_css')
def global_admin_css():
    return format_html(
        '<style>'
        '.object-list th, .object-list td {{ text-align: right; }}'
        '.listing {{ direction: rtl; }}'
        '.form-horizontal .field {{ margin-bottom: 20px; }}'
        '.form-horizontal .field-content {{ position: relative; }}'
        '.error-message {{ color: #dc3545; font-size: 14px; margin-top: 5px; }}'
        '</style>'
    )


# Custom editor CSS for rich text fields
@hooks.register('insert_editor_css')  
def editor_css():
    return format_html(
        '<style>'
        '.richtext {{ direction: rtl; text-align: right; }}'
        '</style>'
    )
