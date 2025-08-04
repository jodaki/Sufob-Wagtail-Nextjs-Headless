from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.http import JsonResponse
from .models import Transaction, DailyInfo
# API: لیست معاملات با فیلتر تاریخ و کالا (public, no auth)
@csrf_exempt
def api_transactions(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    commodity = request.GET.get('commodity')
    
    qs = Transaction.objects.all().order_by('-transaction_date')
    
    if from_date:
        qs = qs.filter(transaction_date__gte=from_date)
    if to_date:
        qs = qs.filter(transaction_date__lte=to_date)
    if commodity:
        qs = qs.filter(commodity_name__icontains=commodity)
    
    data = [
        {
            'id': t.id,
            'commodity_name': t.commodity_name,
            'symbol': t.symbol,
            'hall': t.hall,
            'producer': t.producer,
            'contract_type': t.contract_type,
            'final_price': t.final_price,
            'transaction_value': t.transaction_value,
            'lowest_price': t.lowest_price,
            'highest_price': t.highest_price,
            'base_price': t.base_price,
            'offer_volume': t.offer_volume,
            'demand_volume': t.demand_volume,
            'contract_volume': t.contract_volume,
            'unit': t.unit,
            'transaction_date': t.transaction_date,
            'supplier': t.supplier,
            'broker': t.broker,
            'settlement_type': t.settlement_type,
        }
        for t in qs[:100]
    ]
    return JsonResponse({'results': data})

# API: لیست کالاهای موجود (public, no auth)
@csrf_exempt
def api_commodities(request):
    commodities = Transaction.objects.values_list('commodity_name', flat=True).distinct()
    data = [{'name': commodity} for commodity in commodities if commodity]
    return JsonResponse({'results': data})

from django.http import JsonResponse
from .models import DailyInfo
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


from django.views.decorators.csrf import csrf_exempt
# API: لیست اطلاعات روزانه (public, no auth)
@csrf_exempt
def api_dailyinfo_list(request):
    infos = DailyInfo.objects.order_by('-transaction_date')[:100]
    data = [
        {
            'id': info.id,
            'avg_final_price': info.avg_final_price,
            'final_price': info.final_price,
            'lowest_price': info.lowest_price,
            'highest_price': info.highest_price,
            'weekly_range': info.weekly_range,
            'monthly_range': info.monthly_range,
            'monthly_change': info.monthly_change,
            'settlement_type': info.settlement_type,
            'transaction_date': info.transaction_date,
            'contract_volume': info.contract_volume,
            'demand': info.demand,
            'offer_volume': info.offer_volume,
            'base_price': info.base_price,
            'transaction_value': info.transaction_value,
        }
        for info in infos
    ]
    return JsonResponse({'results': data})


# API: جزئیات یک رکورد اطلاعات روزانه (نیازمند توکن)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_dailyinfo_detail(request, pk):
    try:
        info = DailyInfo.objects.get(pk=pk)
        data = {
            'id': info.id,
            'avg_final_price': info.avg_final_price,
            'final_price': info.final_price,
            'lowest_price': info.lowest_price,
            'highest_price': info.highest_price,
            'weekly_range': info.weekly_range,
            'monthly_range': info.monthly_range,
            'monthly_change': info.monthly_change,
            'settlement_type': info.settlement_type,
            'transaction_date': info.transaction_date,
            'contract_volume': info.contract_volume,
            'demand': info.demand,
            'offer_volume': info.offer_volume,
            'base_price': info.base_price,
            'transaction_value': info.transaction_value,
        }
        return JsonResponse(data)
    except DailyInfo.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

# API: دریافت یا ساخت توکن برای کاربر لاگین شده
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def api_get_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = User.objects.filter(username=username).first()
    if user and user.check_password(password):
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key})
    return JsonResponse({'error': 'نام کاربری یا رمز عبور اشتباه است'}, status=400)
from .models import DailyInfo
from django.shortcuts import render

def dailyinfo_public(request):
    infos = DailyInfo.objects.order_by('-transaction_date')[:30]
    return render(request, 'transactions/dailyinfo_public.html', {'infos': infos})

from django.shortcuts import render
from .models import Transaction

def home(request):
    return render(request, 'transactions/home.html')

def iron_concentrate(request):
    # نمایش همه رکوردهای Transaction بدون فیلتر
    transactions = Transaction.objects.all().order_by('-transaction_date')
    return render(request, 'transactions/iron_concentrate.html', {'transactions': transactions})
