from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup
from wagtail import hooks
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import AllData, DailyData, WeeklyData, MonthlyData, YearlyData, DataAggregationLog


class AllDataAdmin(ModelAdmin):
    model = AllData
    menu_label = 'تمام داده‌ها'
    menu_icon = 'list-ul'
    list_display = ['symbol', 'company_name', 'trade_date_shamsi', 'final_price', 'contracts_volume', 'trade_value']
    list_filter = ['trade_date', 'symbol', 'source', 'created_at']
    search_fields = ['symbol', 'company_name', 'isin', 'trade_date_shamsi']
    ordering = ['-trade_date', 'symbol']
    list_per_page = 50
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


class AllDataAdmin(ModelAdmin):
    model = AllData
    menu_label = 'تمام داده‌ها (All Data)'
    menu_icon = 'table'
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['symbol_name', 'symbol_code', 'trade_date_shamsi', 'last_price', 'trade_volume', 'trade_value', 'created_at']
    list_filter = ['trade_date_gregorian', 'market_code', 'group_code', 'state']
    search_fields = ['symbol_name', 'symbol_code', 'company_name']
    ordering = ['-trade_date_gregorian', 'symbol_code']
    list_per_page = 50
    
    def get_extra_attrs_for_field_col(self, obj, field_name):
        if field_name == 'trade_date_shamsi':
            return {'class': 'title'}
        return super().get_extra_attrs_for_field_col(obj, field_name)


class DailyDataAdmin(ModelAdmin):
    model = DailyData
    menu_label = 'داده‌های روزانه'
    menu_icon = 'date'
    list_display = ['trade_date_shamsi', 'avg_final_price', 'min_price', 'max_price', 'total_trade_value', 'records_count']
    list_filter = ['trade_date', 'created_at']
    search_fields = ['trade_date_shamsi']
    ordering = ['-trade_date']
    list_per_page = 20


class WeeklyDataAdmin(ModelAdmin):
    model = WeeklyData
    menu_label = 'داده‌های هفتگی'
    menu_icon = 'date'
    list_display = ['__str__', 'avg_final_price', 'min_price', 'max_price', 'total_trade_value', 'records_count']
    list_filter = ['year', 'week_number']
    ordering = ['-year', '-week_number']
    list_per_page = 20


class MonthlyDataAdmin(ModelAdmin):
    model = MonthlyData
    menu_label = 'داده‌های ماهانه'
    menu_icon = 'date'
    list_display = ['month_shamsi', 'avg_final_price', 'min_price', 'max_price', 'total_trade_value', 'records_count']
    list_filter = ['year', 'month']
    ordering = ['-year', '-month']
    list_per_page = 12


class YearlyDataAdmin(ModelAdmin):
    model = YearlyData
    menu_label = 'داده‌های سالانه'
    menu_icon = 'date'
    list_display = ['year', 'avg_final_price', 'min_price', 'max_price', 'total_trade_value', 'records_count']
    list_filter = ['year']
    ordering = ['-year']
    list_per_page = 10


class DataAggregationLogAdmin(ModelAdmin):
    model = DataAggregationLog
    menu_label = 'لاگ تجمیع داده‌ها'
    menu_icon = 'list-ul'
    list_display = ['aggregation_type', 'start_time', 'success_icon', 'records_processed', 'records_created', 'duration_display']
    list_filter = ['aggregation_type', 'success', 'start_time']
    ordering = ['-start_time']
    list_per_page = 20
    
    def success_icon(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">✅ موفق</span>')
        else:
            return format_html('<span style="color: red;">❌ ناموفق</span>')
    success_icon.short_description = 'وضعیت'
    
    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            seconds = duration.total_seconds()
            if seconds < 60:
                return f"{seconds:.1f} ثانیه"
            else:
                minutes = seconds / 60
                return f"{minutes:.1f} دقیقه"
        return "-"
    duration_display.short_description = 'مدت زمان'


class DataManagementGroup(ModelAdminGroup):
    menu_label = 'مدیریت داده‌ها (Data Management)'
    menu_icon = 'view'
    menu_order = 200
    items = (AllDataAdmin, DailyDataAdmin, WeeklyDataAdmin, MonthlyDataAdmin, YearlyDataAdmin, DataAggregationLogAdmin)


# ثبت گروه در Wagtail Admin
modeladmin_register(DataManagementGroup)


# اضافه کردن دکمه‌های عملیاتی به admin
@hooks.register('register_admin_urls')
def register_data_management_urls():
    return [
        path('data-management/aggregate/', aggregate_data_view, name='data_management_aggregate'),
        path('data-management/dashboard/', dashboard_view, name='data_management_dashboard'),
    ]


def aggregate_data_view(request):
    """ویو برای اجرای دستی تجمیع داده‌ها"""
    from django.contrib import messages
    from django.core.management import call_command
    
    if request.method == 'POST':
        aggregation_type = request.POST.get('type', 'all')
        try:
            call_command('aggregate_price_data', type=aggregation_type)
            messages.success(request, f'تجمیع داده‌های {aggregation_type} با موفقیت انجام شد.')
        except Exception as e:
            messages.error(request, f'خطا در تجمیع داده‌ها: {str(e)}')
    
    return HttpResponseRedirect(reverse('wagtailadmin_home'))


def dashboard_view(request):
    """داشبورد مدیریت داده‌ها"""
    from django.shortcuts import render
    
    context = {
        'daily_count': DailyData.objects.count(),
        'weekly_count': WeeklyData.objects.count(),
        'monthly_count': MonthlyData.objects.count(),
        'yearly_count': YearlyData.objects.count(),
        'latest_logs': DataAggregationLog.objects.all()[:10],
    }
    
    return render(request, 'data_management/dashboard.html', context)


# اضافه کردن دکمه‌ها به menu
@hooks.register('register_admin_menu_item')
def register_aggregate_menu_item():
    from wagtail.admin.menu import MenuItem
    
    return MenuItem(
        'تجمیع داده‌ها', 
        reverse('data_management_aggregate'),
        classnames='icon icon-cogs',
        order=400
    )
