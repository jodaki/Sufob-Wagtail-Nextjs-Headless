from data_management.models import (
    AllData, 
    CommodityDailyPriceSeries,
    CommodityWeeklyPriceSeries,
    CommodityMonthlyPriceSeries,
    CommodityYearlyPriceSeries
)
from wagtail.api.v2.filters import FieldsFilter
from wagtail.api.v2.views import BaseAPIViewSet
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from price_display.models import PricePage
import jdatetime
from datetime import datetime, date
from wagtail.models import Page


class TransactionAPIViewSet(BaseAPIViewSet):
    """API ViewSet برای دریافت داده‌های معاملات"""
    model = AllData
    known_query_parameters = BaseAPIViewSet.known_query_parameters.union([
        "commodity", "from_date", "to_date"
    ])

    listing_default_fields = BaseAPIViewSet.listing_default_fields + [
        "commodity_name",
        "symbol", 
        "final_price",
        "base_price",
        "transaction_date",
        "contract_volume",
        "producer",
        "settlement_type",
    ]

    filter_backends = BaseAPIViewSet.filter_backends + [FieldsFilter]

    def get_queryset(self):
        queryset = AllData.objects.all().order_by('-transaction_date')
        
        # فیلتر بر اساس کالا
        commodity = self.request.GET.get('commodity')
        if commodity:
            queryset = queryset.filter(commodity_name__icontains=commodity)
            
        # فیلتر بر اساس تاریخ
        from_date = self.request.GET.get('from_date')
        if from_date:
            queryset = queryset.filter(transaction_date__gte=from_date)
            
        to_date = self.request.GET.get('to_date')
        if to_date:
            queryset = queryset.filter(transaction_date__lte=to_date)
            
        return queryset


class CommodityAPIViewSet(BaseAPIViewSet):
    """API ViewSet برای دریافت لیست کالاها"""
    # Ensure router sees a class for issubclass checks
    model = Page
    
    def list(self, request):
        commodities = AllData.objects.values_list('commodity_name', flat=True).distinct()
        data = [{'name': commodity} for commodity in commodities if commodity]
        return Response({'items': data})


@csrf_exempt
def price_chart_data(request, commodity):
    """API endpoint برای دریافت داده‌های چارت"""
    try:
        transactions = AllData.objects.filter(
            commodity_name__icontains=commodity
        ).order_by('-transaction_date')[:30]
        
        chart_data = []
        for transaction in transactions:
            chart_data.append({
                'time': transaction.transaction_date,
                'value': float(transaction.final_price or transaction.base_price or 0),
                'volume': transaction.contract_volume or 0,
            })
        
        # Sort by date for proper chart display
        chart_data = sorted(chart_data, key=lambda x: x['time'])
        
        return JsonResponse({
            'commodity': commodity,
            'data': chart_data,
            'count': len(chart_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class PriceSeriesAPIViewSet(BaseAPIViewSet):
    """
    API endpoint برای بازگرداندن سری‌های زمانی سازگار با TradingView Lightweight Charts
    پارامترها:
      - page: شناسه عددی صفحه یا slug آن (PricePage)
      - period: یکی از daily|weekly|monthly|yearly|all (پیش‌فرض all)
      - days: تعداد روزهای اخیر برای daily (در صورت عدم ارسال، از chart_days صفحه استفاده می‌شود)
    خروجی:
      - برای period=all => {'periods': {'daily': [...], 'weekly': [...], 'monthly': [...], 'yearly': [...]}}
      - برای period خاص => {'period': 'daily', 'series': [...]} که هر آیتم {'time': unix_ts, 'value': float}
    """

    # Ensure router sees a class for issubclass checks
    model = Page

    known_query_parameters = BaseAPIViewSet.known_query_parameters.union({
        "page", "period", "days"
    })

    def get_queryset(self):
        # Return empty queryset since we override listing_view method completely
        return Page.objects.none()

    def listing_view(self, request):
        """Override listing_view to return optimized pre-computed series data"""
        page_param = request.GET.get('page')
        period = (request.GET.get('period') or 'all').lower()
        days_param = request.GET.get('days')

        if not page_param:
            return Response({"error": "Missing 'page' parameter (id or slug)."}, status=400)

        # تلاش برای یافتن PricePage بر اساس id یا slug
        page_obj = None
        try:
            page_id = int(page_param)
            page_obj = PricePage.objects.filter(id=page_id).first()
        except ValueError:
            page_obj = PricePage.objects.filter(slug=page_param).first()

        if not page_obj:
            return Response({"error": "PricePage not found."}, status=404)

        try:
            days = int(days_param) if days_param else int(page_obj.chart_days or 30)
        except Exception:
            days = 30

        # دریافت نام کالا از صفحه
        commodity_name = None
        if hasattr(page_obj, 'subcategory') and page_obj.subcategory:
            commodity_name = page_obj.subcategory.name
        
        if not commodity_name:
            return Response({"error": "Commodity name not found for this page."}, status=404)

        def unix_ts(date_obj: date):
            """تبدیل تاریخ به timestamp برای TradingView"""
            if not date_obj:
                return None
            dt = datetime(date_obj.year, date_obj.month, date_obj.day)
            return int(dt.timestamp())

        def get_daily_series(limit_days=None):
            """دریافت سری روزانه از جدول پیش‌پردازش شده"""
            queryset = CommodityDailyPriceSeries.objects.filter(
                commodity_name=commodity_name
            ).order_by('-trade_date')
            
            if limit_days:
                queryset = queryset[:limit_days]
            
            series = []
            for item in queryset:
                ts = unix_ts(item.trade_date)
                if ts:
                    series.append({
                        'time': ts,
                        'value': float(item.avg_price) if item.avg_price else 0,
                        'open': float(item.min_price) if item.min_price else 0,
                        'high': float(item.max_price) if item.max_price else 0,
                        'low': float(item.min_price) if item.min_price else 0,
                        'close': float(item.avg_price) if item.avg_price else 0,
                        'volume': item.total_volume or 0,
                        'transactions': item.transaction_count or 0
                    })
            
            # مرتب کردن بر اساس زمان (قدیمی‌ترین اول)
            return sorted(series, key=lambda x: x['time'])

        def get_weekly_series():
            """دریافت سری هفتگی از جدول پیش‌پردازش شده"""
            queryset = CommodityWeeklyPriceSeries.objects.filter(
                commodity_name=commodity_name
            ).order_by('-year', '-week_number')
            
            series = []
            for item in queryset:
                ts = unix_ts(item.week_start_date)
                if ts:
                    series.append({
                        'time': ts,
                        'value': float(item.avg_price) if item.avg_price else 0,
                        'open': float(item.min_price) if item.min_price else 0,
                        'high': float(item.max_price) if item.max_price else 0,
                        'low': float(item.min_price) if item.min_price else 0,
                        'close': float(item.avg_price) if item.avg_price else 0,
                        'volume': item.total_volume or 0,
                        'transactions': item.transaction_count or 0
                    })
            
            return sorted(series, key=lambda x: x['time'])

        def get_monthly_series():
            """دریافت سری ماهانه از جدول پیش‌پردازش شده"""
            queryset = CommodityMonthlyPriceSeries.objects.filter(
                commodity_name=commodity_name
            ).order_by('-year', '-month')
            
            series = []
            for item in queryset:
                # ایجاد تاریخ اول ماه میلادی از سال و ماه شمسی
                try:
                    # تبدیل سال و ماه شمسی به میلادی
                    jalali_date = jdatetime.date(item.year, item.month, 1)
                    gregorian_date = jalali_date.togregorian()
                    ts = unix_ts(gregorian_date)
                    
                    if ts:
                        series.append({
                            'time': ts,
                            'value': float(item.avg_price) if item.avg_price else 0,
                            'open': float(item.min_price) if item.min_price else 0,
                            'high': float(item.max_price) if item.max_price else 0,
                            'low': float(item.min_price) if item.min_price else 0,
                            'close': float(item.avg_price) if item.avg_price else 0,
                            'volume': item.total_volume or 0,
                            'transactions': item.transaction_count or 0
                        })
                except Exception:
                    continue
            
            return sorted(series, key=lambda x: x['time'])

        def get_yearly_series():
            """دریافت سری سالانه از جدول پیش‌پردازش شده"""
            queryset = CommodityYearlyPriceSeries.objects.filter(
                commodity_name=commodity_name
            ).order_by('-year')
            
            series = []
            for item in queryset:
                try:
                    # ایجاد تاریخ اول سال میلادی از سال شمسی
                    jalali_date = jdatetime.date(item.year, 1, 1)
                    gregorian_date = jalali_date.togregorian()
                    ts = unix_ts(gregorian_date)
                    
                    if ts:
                        series.append({
                            'time': ts,
                            'value': float(item.avg_price) if item.avg_price else 0,
                            'open': float(item.min_price) if item.min_price else 0,
                            'high': float(item.max_price) if item.max_price else 0,
                            'low': float(item.min_price) if item.min_price else 0,
                            'close': float(item.avg_price) if item.avg_price else 0,
                            'volume': item.total_volume or 0,
                            'transactions': item.transaction_count or 0
                        })
                except Exception:
                    continue
            
            return sorted(series, key=lambda x: x['time'])

        # پاسخ بر اساس period درخواست شده
        if period == 'daily':
            return Response({
                'page_id': page_obj.id,
                'slug': page_obj.slug,
                'commodity_name': commodity_name,
                'period': 'daily',
                'series': get_daily_series(days)
            })
        elif period == 'weekly':
            return Response({
                'page_id': page_obj.id,
                'slug': page_obj.slug,
                'commodity_name': commodity_name,
                'period': 'weekly',
                'series': get_weekly_series()
            })
        elif period == 'monthly':
            return Response({
                'page_id': page_obj.id,
                'slug': page_obj.slug,
                'commodity_name': commodity_name,
                'period': 'monthly',
                'series': get_monthly_series()
            })
        elif period == 'yearly':
            return Response({
                'page_id': page_obj.id,
                'slug': page_obj.slug,
                'commodity_name': commodity_name,
                'period': 'yearly',
                'series': get_yearly_series()
            })

        # پیش‌فرض: بازگرداندن همه دوره‌ها
        return Response({
            'page_id': page_obj.id,
            'slug': page_obj.slug,
            'commodity_name': commodity_name,
            'periods': {
                'daily': get_daily_series(days),
                'weekly': get_weekly_series(),
                'monthly': get_monthly_series(),
                'yearly': get_yearly_series(),
            }
        })
