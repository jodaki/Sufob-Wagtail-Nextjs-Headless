from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register, ModelAdminGroup
from wagtail import hooks
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import AllData, DailyData, WeeklyData, MonthlyData, YearlyData, DataAggregationLog


class AllDataAdmin(ModelAdmin):
    model = AllData
    menu_label = 'همه رکوردها (All Records)'
    menu_icon = 'table'
    menu_order = 100
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['commodity_name', 'symbol', 'transaction_date', 'final_price', 'contract_volume', 'transaction_value', 'created_at']
    list_filter = ['transaction_date', 'commodity_name', 'source', 'created_at']
    search_fields = ['commodity_name', 'symbol', 'producer', 'supplier']
    ordering = ['-transaction_date', 'symbol']
    list_per_page = 50
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()


class DailyDataAdmin(ModelAdmin):
    model = DailyData
    menu_label = 'روزانه (Daily)'
    menu_icon = 'date'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['trade_date', 'trade_date_shamsi', 'avg_final_price', 'avg_weighted_final_price', 'total_contracts_volume', 'records_count']
    list_filter = ['trade_date']
    search_fields = ['trade_date_shamsi']
    ordering = ['-trade_date']
    list_per_page = 50


class WeeklyDataAdmin(ModelAdmin):
    model = WeeklyData
    menu_label = 'هفتگی (Weekly)'
    menu_icon = 'view'
    menu_order = 300
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['week_start_date', 'week_end_date', 'year', 'week_number', 'avg_final_price', 'total_contracts_volume', 'records_count']
    list_filter = ['year', 'week_start_date']
    ordering = ['-week_start_date']
    list_per_page = 50


class MonthlyDataAdmin(ModelAdmin):
    model = MonthlyData
    menu_label = 'ماهانه (Monthly)'
    menu_icon = 'calendar'
    menu_order = 400
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['month_shamsi', 'year', 'month', 'avg_final_price', 'total_contracts_volume', 'records_count']
    list_filter = ['year', 'month']
    ordering = ['-year', '-month']
    list_per_page = 50


class YearlyDataAdmin(ModelAdmin):
    model = YearlyData
    menu_label = 'سالانه (Yearly)'
    menu_icon = 'date'
    menu_order = 500
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['year', 'avg_final_price', 'total_contracts_volume', 'records_count']
    list_filter = ['year']
    ordering = ['-year']
    list_per_page = 50


class DataAggregationLogAdmin(ModelAdmin):
    model = DataAggregationLog
    menu_label = 'لاگ تجمیع (Aggregation Log)'
    menu_icon = 'doc-full'
    menu_order = 600
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = ['aggregation_type', 'start_time', 'end_time', 'success', 'records_processed']
    list_filter = ['aggregation_type', 'success', 'start_time']
    ordering = ['-start_time']
    list_per_page = 50


class DataManagementGroup(ModelAdminGroup):
    menu_label = 'مدیریت داده‌ها'
    menu_icon = 'folder-open-inverse'
    menu_order = 200
    items = (AllDataAdmin, DailyDataAdmin, WeeklyDataAdmin, MonthlyDataAdmin, YearlyDataAdmin, DataAggregationLogAdmin)


# ثبت گروه مدل‌ها در Wagtail Admin
modeladmin_register(DataManagementGroup)


# اضافه کردن دکمه‌های عملیاتی به admin
@hooks.register('register_admin_urls')
def register_data_management_urls():
    # Redirect URL for AllData model list and dashboard
    return [
        path('data-management/alldata/', redirect_to_alldata, name='data_management_alldata_redirect'),
        path('data-management/dashboard/', dashboard_view, name='data_management_dashboard'),
    ]


def dashboard_view(request):
    """داشبورد مدیریت داده‌ها"""
    from django.shortcuts import render
    
    context = {
        'alldata_count': AllData.objects.count(),
        'latest_data': AllData.objects.all()[:10],
    }
    
    return render(request, 'data_management/dashboard.html', context)


def redirect_to_alldata(request):
    """
    Redirect to the AllData ModelAdmin index page
    """
    return HttpResponseRedirect(reverse('data_management_alldata_index'))


# اضافه کردن دکمه به menu
@hooks.register('register_admin_menu_item')
def register_data_dashboard_menu_item():
    from wagtail.admin.menu import MenuItem
    
    return MenuItem(
        'داشبورد داده‌ها', 
        reverse('data_management_dashboard'),
        classnames='icon icon-view',
        order=400
    )
