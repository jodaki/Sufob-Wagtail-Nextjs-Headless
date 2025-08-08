from django.shortcuts import render
from django.http import JsonResponse
from .models import AllData, DailyData, WeeklyData, MonthlyData, YearlyData, DataAggregationLog


def data_summary_view(request):
    """نمایش خلاصه‌ای از تمام داده‌ها"""
    
    summary = {
        'all_records': AllData.objects.count(),
        'daily_records': DailyData.objects.count(),
        'weekly_records': WeeklyData.objects.count(),
        'monthly_records': MonthlyData.objects.count(),
        'yearly_records': YearlyData.objects.count(),
        'aggregation_logs': DataAggregationLog.objects.count(),
    }
    
    latest_data = {
        'latest_all_data': list(AllData.objects.order_by('-created_at')[:5].values(
            'commodity_name', 'symbol', 'transaction_date', 'final_price', 'created_at'
        )),
        'latest_daily': list(DailyData.objects.order_by('-trade_date')[:5].values(
            'trade_date', 'trade_date_shamsi', 'avg_final_price', 'records_count'
        )),
        'latest_weekly': list(WeeklyData.objects.order_by('-week_start_date')[:5].values(
            'week_start_date', 'week_end_date', 'avg_final_price', 'records_count'
        )),
        'latest_monthly': list(MonthlyData.objects.order_by('-year', '-month')[:5].values(
            'month_shamsi', 'avg_final_price', 'records_count'
        )),
        'latest_yearly': list(YearlyData.objects.order_by('-year')[:5].values(
            'year', 'avg_final_price', 'records_count'
        )),
    }
    
    context = {
        'summary': summary,
        'latest_data': latest_data,
        'title': 'خلاصه مدیریت داده‌ها'
    }
    
    if request.accepts('application/json'):
        return JsonResponse({
            'summary': summary,
            'latest_data': latest_data
        })
    
    return render(request, 'data_management/data_summary.html', context)


def all_data_list_view(request):
    """نمایش لیست تمام رکوردها"""
    page = int(request.GET.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    records = AllData.objects.order_by('-created_at')[offset:offset + per_page]
    total = AllData.objects.count()
    
    context = {
        'records': records,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': offset + per_page < total,
        'has_prev': page > 1,
        'title': 'همه رکوردها (All Records)'
    }
    
    return render(request, 'data_management/all_data_list.html', context)


def daily_data_list_view(request):
    """نمایش لیست داده‌های روزانه"""
    page = int(request.GET.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    records = DailyData.objects.order_by('-trade_date')[offset:offset + per_page]
    total = DailyData.objects.count()
    
    context = {
        'records': records,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': offset + per_page < total,
        'has_prev': page > 1,
        'title': 'داده‌های روزانه (Daily)'
    }
    
    return render(request, 'data_management/daily_data_list.html', context)


def weekly_data_list_view(request):
    """نمایش لیست داده‌های هفتگی"""
    page = int(request.GET.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    records = WeeklyData.objects.order_by('-week_start_date')[offset:offset + per_page]
    total = WeeklyData.objects.count()
    
    context = {
        'records': records,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': offset + per_page < total,
        'has_prev': page > 1,
        'title': 'داده‌های هفتگی (Weekly)'
    }
    
    return render(request, 'data_management/weekly_data_list.html', context)


def monthly_data_list_view(request):
    """نمایش لیست داده‌های ماهانه"""
    page = int(request.GET.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    records = MonthlyData.objects.order_by('-year', '-month')[offset:offset + per_page]
    total = MonthlyData.objects.count()
    
    context = {
        'records': records,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': offset + per_page < total,
        'has_prev': page > 1,
        'title': 'داده‌های ماهانه (Monthly)'
    }
    
    return render(request, 'data_management/monthly_data_list.html', context)


def yearly_data_list_view(request):
    """نمایش لیست داده‌های سالانه"""
    page = int(request.GET.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page
    
    records = YearlyData.objects.order_by('-year')[offset:offset + per_page]
    total = YearlyData.objects.count()
    
    context = {
        'records': records,
        'total': total,
        'page': page,
        'per_page': per_page,
        'has_next': offset + per_page < total,
        'has_prev': page > 1,
        'title': 'داده‌های سالانه (Yearly)'
    }
    
    return render(request, 'data_management/yearly_data_list.html', context)
