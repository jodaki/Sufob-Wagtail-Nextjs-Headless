from django.contrib import admin
from .models import AllData


@admin.register(AllData)
class AllDataAdmin(admin.ModelAdmin):
    list_display = ['symbol_name', 'symbol_code', 'trade_date_shamsi', 'last_price', 'trade_volume', 'trade_value', 'created_at']
    list_filter = ['trade_date_gregorian', 'market_code', 'group_code', 'state']
    search_fields = ['symbol_name', 'symbol_code', 'company_name']
    ordering = ['-trade_date_gregorian', 'symbol_code']
    date_hierarchy = 'trade_date_gregorian'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات نماد', {
            'fields': ('symbol_code', 'symbol_name', 'company_name', 'market_code', 'group_code', 'state')
        }),
        ('قیمت‌ها', {
            'fields': ('last_price', 'close_price', 'first_price', 'min_price', 'max_price', 'yesterday_price')
        }),
        ('حجم و ارزش', {
            'fields': ('trade_count', 'trade_volume', 'trade_value')
        }),
        ('تاریخ', {
            'fields': ('trade_date_shamsi', 'trade_date_gregorian')
        }),
        ('متادیتا', {
            'fields': ('created_at', 'updated_at', 'raw_data'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DailyData)
class DailyDataAdmin(admin.ModelAdmin):
    list_display = [
        'trade_date_shamsi', 'avg_weighted_final_price', 'avg_final_price',
        'min_price', 'max_price', 'total_trade_value', 'records_count'
    ]
    list_filter = ['trade_date', 'created_at']
    search_fields = ['trade_date_shamsi']
    date_hierarchy = 'trade_date'
    ordering = ['-trade_date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات تاریخ', {
            'fields': ('trade_date', 'trade_date_shamsi')
        }),
        ('قیمت‌ها', {
            'fields': ('avg_weighted_final_price', 'avg_final_price', 
                      'min_price', 'max_price', 'avg_base_price')
        }),
        ('حجم‌ها', {
            'fields': ('total_contracts_volume', 'total_supply_volume', 
                      'total_demand_volume')
        }),
        ('ارزش و نسبت‌ها', {
            'fields': ('total_trade_value', 'buyer_seller_power_ratio')
        }),
        ('متادیتا', {
            'fields': ('records_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(WeeklyData)
class WeeklyDataAdmin(admin.ModelAdmin):
    list_display = [
        'week_display', 'avg_weighted_final_price', 'min_price', 
        'max_price', 'total_trade_value', 'records_count'
    ]
    list_filter = ['year', 'created_at']
    ordering = ['-year', '-week_number']
    readonly_fields = ['created_at', 'updated_at']
    
    def week_display(self, obj):
        return f"هفته {obj.week_number} سال {obj.year}"
    week_display.short_description = "هفته"
    week_display.admin_order_field = 'week_number'


@admin.register(MonthlyData)
class MonthlyDataAdmin(admin.ModelAdmin):
    list_display = [
        'month_shamsi', 'avg_weighted_final_price', 'min_price',
        'max_price', 'total_trade_value', 'records_count'
    ]
    list_filter = ['year', 'month', 'created_at']
    ordering = ['-year', '-month']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(YearlyData)
class YearlyDataAdmin(admin.ModelAdmin):
    list_display = [
        'year', 'avg_weighted_final_price', 'min_price',
        'max_price', 'total_trade_value', 'records_count'
    ]
    list_filter = ['year', 'created_at']
    ordering = ['-year']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DataAggregationLog)
class DataAggregationLogAdmin(admin.ModelAdmin):
    list_display = [
        'aggregation_type', 'start_time', 'duration_display', 
        'records_processed', 'success_display'
    ]
    list_filter = ['aggregation_type', 'success', 'start_time']
    readonly_fields = ['start_time', 'end_time', 'duration_display']
    ordering = ['-start_time']
    
    def duration_display(self, obj):
        if obj.duration:
            return f"{obj.duration.total_seconds():.1f} ثانیه"
        return "نامشخص"
    duration_display.short_description = "مدت زمان"
    
    def success_display(self, obj):
        return "✅ موفق" if obj.success else "❌ ناموفق"
    success_display.short_description = "وضعیت"
    success_display.admin_order_field = 'success'
    
    fieldsets = (
        ('اطلاعات کلی', {
            'fields': ('aggregation_type', 'start_time', 'end_time', 'duration_display')
        }),
        ('آمار', {
            'fields': ('records_processed', 'records_created', 'records_updated')
        }),
        ('وضعیت', {
            'fields': ('success', 'error_message')
        })
    )
