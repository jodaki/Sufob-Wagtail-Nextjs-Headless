from django.contrib import admin
from .models import Category, PriceData, DataImportLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'parent', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active', 'order']
    ordering = ['order', 'name']
    date_hierarchy = 'created_at'


# PriceData و DataImportLog را فعلاً comment می‌کنیم تا تداخل نداشته باشیم
# @admin.register(PriceData)
# class PriceDataAdmin(admin.ModelAdmin):
#     list_display = ['commodity_name', 'symbol', 'final_price', 'price_date', 'volume', 'source', 'created_at']
#     list_filter = ['commodity_name', 'source', 'price_date', 'created_at']
#     search_fields = ['commodity_name', 'symbol']
#     date_hierarchy = 'price_date'
#     readonly_fields = ['created_at', 'updated_at']
#     ordering = ['-price_date', 'commodity_name']


# @admin.register(DataImportLog)
# class DataImportLogAdmin(admin.ModelAdmin):
#     list_display = ['commodity_name', 'start_date', 'end_date', 'status', 'total_records', 'imported_records', 'created_at']
#     list_filter = ['status', 'commodity_name', 'created_at']
#     search_fields = ['commodity_name', 'error_message']
#     readonly_fields = ['created_at', 'updated_at']
#     ordering = ['-created_at']
#     date_hierarchy = 'created_at'
