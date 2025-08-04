from django.contrib import admin
from django.contrib import messages
from .models import Transaction, DailyInfo
import subprocess

def fetch_ime_data_action(modeladmin, request, queryset):
    try:
        result = subprocess.run([
            'python', 'transactions/fetch_ime_data.py'
        ], capture_output=True, text=True)
        if result.returncode == 0:
            messages.success(request, 'داده‌ها با موفقیت استخراج و ذخیره شدند.')
        else:
            messages.error(request, f'خطا در اجرای اسکریپت: {result.stderr}')
    except Exception as e:
        messages.error(request, f'خطای غیرمنتظره: {str(e)}')

fetch_ime_data_action.short_description = 'استخراج و ذخیره معاملات جدید از بورس کالا'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'commodity_name', 'symbol', 'transaction_date', 'final_price', 'transaction_value',
        'producer', 'contract_type', 'unit', 'broker', 'settlement_type', 'delivery_date'
    )
    search_fields = ('commodity_name', 'symbol', 'producer', 'broker')
    list_filter = ('transaction_date', 'producer', 'broker', 'contract_type')
    actions = [fetch_ime_data_action]

class DailyInfoAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date', 'final_price', 'avg_final_price', 'lowest_price', 'highest_price',
        'weekly_range', 'monthly_range', 'monthly_change', 'settlement_type',
        'contract_volume', 'demand', 'offer_volume', 'base_price', 'transaction_value'
    ]
    search_fields = ['transaction_date', 'final_price']
    ordering = ['-transaction_date']

admin.site.register(DailyInfo, DailyInfoAdmin)
