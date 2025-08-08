from django.contrib import admin
from .models import AllData


@admin.register(AllData)
class AllDataAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'commodity_name', 'transaction_date', 'final_price', 'contract_volume', 'transaction_value', 'created_at']
    list_filter = ['transaction_date', 'source', 'created_at']
    search_fields = ['symbol', 'commodity_name', 'producer', 'supplier']
    ordering = ['-transaction_date', 'symbol']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('commodity_name', 'symbol', 'producer', 'hall')
        }),
        ('قیمت‌ها', {
            'fields': ('final_price', 'base_price', 'lowest_price', 'highest_price', 'transaction_value')
        }),
        ('حجم‌ها', {
            'fields': ('contract_volume', 'offer_volume', 'demand_volume', 'unit')
        }),
        ('تاریخ', {
            'fields': ('transaction_date',)
        }),
        ('اطلاعات اضافی', {
            'fields': ('supplier', 'broker', 'settlement_type', 'contract_type'),
            'classes': ('collapse',)
        }),
        ('متادیتا', {
            'fields': ('source', 'api_endpoint', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
