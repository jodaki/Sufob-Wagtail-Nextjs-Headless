from transactions.models import Transaction
from wagtail.api.v2.filters import FieldsFilter
from wagtail.api.v2.views import BaseAPIViewSet
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class TransactionAPIViewSet(BaseAPIViewSet):
    """API ViewSet برای دریافت داده‌های معاملات"""
    model = Transaction
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
        queryset = Transaction.objects.all().order_by('-transaction_date')
        
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
    
    def list(self, request):
        commodities = Transaction.objects.values_list('commodity_name', flat=True).distinct()
        data = [{'name': commodity} for commodity in commodities if commodity]
        return Response({'items': data})


@csrf_exempt
def price_chart_data(request, commodity):
    """API endpoint برای دریافت داده‌های چارت"""
    try:
        transactions = Transaction.objects.filter(
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
