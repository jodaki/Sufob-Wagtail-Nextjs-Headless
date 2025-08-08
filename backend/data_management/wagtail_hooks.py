from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail import hooks
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import AllData


class AllDataAdmin(ModelAdmin):
    model = AllData
    menu_label = 'تمام داده‌ها (All Data)'
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


# ثبت مدل در Wagtail Admin
modeladmin_register(AllDataAdmin)


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
