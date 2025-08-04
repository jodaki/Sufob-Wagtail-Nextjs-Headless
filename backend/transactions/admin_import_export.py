from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt #add me

from django.shortcuts import render
# ...existing code...
from django.db.models import Sum, Min, Max, F
# ...existing code...

def daily_settings(request):
    auto_process = request.GET.get('auto', 'on') == 'on'
    manual = request.GET.get('manual', None)
    dates = Transaction.objects.values_list('transaction_date', flat=True).distinct()
    to_process = [d for d in dates if not DailyInfo.objects.filter(transaction_date=d).exists()]
    processed_count = DailyInfo.objects.count()
    to_process_count = len(to_process)
    # پردازش خودکار یا دستی
    if auto_process or manual:
        for date in to_process:
            txs = Transaction.objects.filter(transaction_date=date)
            total_volume = txs.aggregate(Sum('contract_volume'))['contract_volume__sum'] or 0
            total_demand = txs.aggregate(Sum('demand_volume'))['demand_volume__sum'] or 0
            total_offer = txs.aggregate(Sum('offer_volume'))['offer_volume__sum'] or 0
            total_value = txs.aggregate(Sum('transaction_value'))['transaction_value__sum'] or 0
            weighted_avg = 0
            sum_price_volume = txs.aggregate(total=Sum(F('final_price') * F('contract_volume')))['total'] or 0
            if total_volume:
                weighted_avg = round(sum_price_volume / total_volume, 2)
            final_price = txs.order_by('-id').first().final_price if txs.exists() else ''
            lowest_price = txs.aggregate(Min('final_price'))['final_price__min'] or ''
            highest_price = txs.aggregate(Max('final_price'))['final_price__max'] or ''
            week_dates = Transaction.objects.filter(transaction_date__lte=date).order_by('-transaction_date').values_list('transaction_date', flat=True)[:7]
            week_prices = list(Transaction.objects.filter(transaction_date__in=week_dates).values_list('final_price', flat=True))
            week_prices = [p for p in week_prices if p is not None]
            week_min = min(week_prices) if week_prices else ''
            week_max = max(week_prices) if week_prices else ''
            month_dates = Transaction.objects.filter(transaction_date__lte=date).order_by('-transaction_date').values_list('transaction_date', flat=True)[:30]
            month_prices = list(Transaction.objects.filter(transaction_date__in=month_dates).values_list('final_price', flat=True))
            month_prices = [p for p in month_prices if p is not None]
            month_min = min(month_prices) if month_prices else ''
            month_max = max(month_prices) if month_prices else ''
            monthly_change = ''
            if len(month_prices) >= 2:
                try:
                    monthly_change = round(((final_price - month_prices[-1]) / month_prices[-1]) * 100, 2)
                except:
                    monthly_change = ''
            base_price = txs.first().base_price if txs.exists() else ''
            settlement_type = txs.first().settlement_type if txs.exists() else ''
            DailyInfo.objects.create(
                avg_final_price=weighted_avg,
                final_price=final_price if final_price not in [None, ''] else 0,
                lowest_price=lowest_price,
                highest_price=highest_price,
                weekly_range=f"{week_min}-{week_max}",
                monthly_range=f"{month_min}-{month_max}",
                monthly_change=monthly_change,
                settlement_type=settlement_type,
                transaction_date=date,
                contract_volume=total_volume,
                demand=total_demand,
                offer_volume=total_offer,
                base_price=base_price,
                transaction_value=total_value
            )
    return render(request, 'admin/daily_settings.html', {
        'auto_process': auto_process,
        'processed_count': processed_count,
        'to_process_count': to_process_count
    })
# گزارشات ورود اطلاعات
from django.views.decorators.http import require_GET, require_POST
def import_logs_view(request):
    from .models import ImportLog
    page = int(request.GET.get('page', 1))
    if request.method == 'POST' and request.GET.get('delete'):
        log_id = request.GET.get('delete')
        ImportLog.objects.filter(id=log_id).delete()
        return redirect(request.path)
    logs = ImportLog.objects.all().order_by('-created_at')
    paginator = Paginator(logs, 10)
    logs_page = paginator.get_page(page)
    from django.contrib.admin.sites import site
    context = dict(site.each_context(request), logs=logs_page, title='گزارشات ورود اطلاعات')
    return TemplateResponse(request, 'admin/import_logs.html', context)
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Transaction, ImportLog, DailyInfo
# ذخیره رکوردها و ثبت گزارش
@csrf_exempt
@require_POST
def import_export_save(request):
    import json
    data = json.loads(request.body)
    product_type = data.get('product_type', 'iron_concentrate')
    duplicate_action = data.get('duplicate_action', 'remove')
    records = data.get('records', [])
    add_type = 'دستی'
    saved_count = 0
    duplicate_count = 0
    status = 'ذخیره شده'
    # معیار تکراری: symbol + transaction_date
    for rec in records:
        symbol = rec.get('symbol') or rec.get('Symbol')
        transaction_date = rec.get('transaction_date') or rec.get('date')
        exists = Transaction.objects.filter(symbol=symbol, transaction_date=transaction_date).first()
        if exists:
            duplicate_count += 1
            if duplicate_action == 'replace':
                exists.delete()
            else:
                continue
        try:
            Transaction.objects.create(
                commodity_name=rec.get('commodity_name') or rec.get('GoodsName'),
                symbol=symbol,
                hall=rec.get('hall') or rec.get('Talar'),
                producer=rec.get('producer') or rec.get('ProducerName'),
                contract_type=rec.get('contract_type') or rec.get('ContractType'),
                final_price=rec.get('final_price') or rec.get('Price'),
                transaction_value=rec.get('transaction_value') or rec.get('TotalPrice') or 0,
                lowest_price=rec.get('lowest_price') or rec.get('MinPrice'),
                highest_price=rec.get('highest_price') or rec.get('MaxPrice'),
                base_price=rec.get('base_price') or rec.get('ArzeBasePrice'),
                offer_volume=rec.get('offer_volume') or rec.get('arze'),
                demand_volume=rec.get('demand_volume') or rec.get('taghaza'),
                contract_volume=rec.get('contract_volume') or rec.get('Quantity'),
                unit=rec.get('unit') or rec.get('Unit'),
                transaction_date=transaction_date,
                supplier=rec.get('supplier') or rec.get('ArzehKonandeh'),
                broker=rec.get('broker') or rec.get('cBrokerSpcName'),
                settlement_type=rec.get('settlement_type') or rec.get('Tasvieh'),
                delivery_date=rec.get('delivery_date') or rec.get('DeliveryDate'),
                warehouse=rec.get('warehouse') or rec.get('Warehouse'),
                settlement_date=rec.get('settlement_date') or rec.get('SettlementDate'),
                x_talar_report_pk=rec.get('x_talar_report_pk') or rec.get('xTalarReportPK'),
                b_arzeh_radif_tar_sarresid=rec.get('b_arzeh_radif_tar_sarresid') or rec.get('bArzehRadifTarSarresid'),
                mode_description=rec.get('mode_description') or rec.get('ModeDescription'),
                method_description=rec.get('method_description') or rec.get('MethodDescription'),
                currency=rec.get('currency') or rec.get('Currency'),
                packet_name=rec.get('packet_name') or rec.get('PacketName'),
                arzeh_pk=rec.get('arzeh_pk') or rec.get('arzehPk'),
            )
            saved_count += 1
        except Exception as e:
            status = 'رد شد'
    ImportLog.objects.create(
        product_type=product_type,
        from_date=records[0].get('transaction_date') if records else '',
        to_date=records[-1].get('transaction_date') if records else '',
        record_count=len(records),
        status=status,
        add_type=add_type
    )
    return JsonResponse({
        'success': True,
        'saved_count': saved_count,
        'duplicate_count': duplicate_count,
        'duplicate_action': duplicate_action
    })

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt
import requests
import json

class JalaliDateForm(forms.Form):
    from_date = forms.CharField(label='تاریخ شروع (شمسی)', widget=forms.TextInput(attrs={'class': 'jalali_date-input'}))
    to_date = forms.CharField(label='تاریخ پایان (شمسی)', widget=forms.TextInput(attrs={'class': 'jalali_date-input'}))

def import_export_view(request):
    from django.contrib.admin.sites import site
    form = JalaliDateForm()
    context = dict(
        site.each_context(request),
        form=form,
        title='Import/Export'
    )
    return TemplateResponse(request, 'admin/import_export.html', context)

@csrf_exempt
def import_export_api(request):
    import json
    from transactions.models import StagedTransaction
    if request.method == 'POST':
        data = json.loads(request.body)
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        url = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList"
        payload = {
            "Language": 8,
            "fari": False,
            "GregorianFromDate": from_date,
            "GregorianToDate": to_date,
            "MainCat": 1,
            "Cat": 49,
            "SubCat": 477,
            "Producer": 0
        }
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "text/plain, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept-Language": "fa-IR,fa;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6"
        }
        log_msgs = []
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            api_data = json.loads(response.json().get("d", "[]"))
            log_msgs.append(f"دریافت داده از API: تعداد رکورد {len(api_data)}")
            saved = 0
            errors = []
            for item in api_data:
                try:
                    st = StagedTransaction.objects.create(
                        commodity_name=item.get("GoodsName", ""),
                        symbol=item.get("Symbol", ""),
                        hall=item.get("Talar", ""),
                        producer=item.get("ProducerName", ""),
                        contract_type=item.get("ContractType", ""),
                        final_price=float(item.get("Price")) if item.get("Price") else None,
                        transaction_value=int(item.get("TotalPrice")) if item.get("TotalPrice") else 0,
                        lowest_price=float(item.get("MinPrice")) if item.get("MinPrice") else None,
                        highest_price=float(item.get("MaxPrice")) if item.get("MaxPrice") else None,
                        base_price=float(item.get("ArzeBasePrice")) if item.get("ArzeBasePrice") else None,
                        offer_volume=int(item.get("arze")) if item.get("arze") else 0,
                        demand_volume=int(item.get("taghaza")) if item.get("taghaza") else 0,
                        contract_volume=int(item.get("Quantity")) if item.get("Quantity") else 0,
                        unit=item.get("Unit", ""),
                        transaction_date=item.get("date", ""),
                        supplier=item.get("ArzehKonandeh", ""),
                        broker=item.get("cBrokerSpcName", ""),
                        settlement_type=item.get("Tasvieh", ""),
                        delivery_date=item.get("DeliveryDate"),
                        warehouse=item.get("Warehouse"),
                        settlement_date=item.get("SettlementDate"),
                        x_talar_report_pk=int(item.get("xTalarReportPK")) if item.get("xTalarReportPK") else None,
                        b_arzeh_radif_tar_sarresid=item.get("bArzehRadifTarSarresid"),
                        mode_description=item.get("ModeDescription"),
                        method_description=item.get("MethodDescription"),
                        currency=item.get("Currency"),
                        packet_name=item.get("PacketName"),
                        arzeh_pk=int(item.get("arzehPk")) if item.get("arzehPk") else None
                    )
                    saved += 1
                except Exception as e:
                    errors.append(str(e))
                    log_msgs.append(f"خطا در ذخیره رکورد: {e}")
            log_msgs.append(f"تعداد رکورد ذخیره شده در StagedTransaction: {saved}")
            log_msgs.append(f"تعداد خطا: {len(errors)}")
            return JsonResponse({
                'success': True,
                'count': len(api_data),
                'sample': api_data[0] if api_data else None,
                'staged_saved': saved,
                'staged_errors': errors,
                'log_msgs': log_msgs
            })
        except Exception as e:
            log_msgs.append(f"خطا در دریافت داده از API: {e}")
            return JsonResponse({'success': False, 'error': str(e), 'log_msgs': log_msgs})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from django.http import JsonResponse
from transactions.models import StagedTransaction, Transaction
from django.views.decorators.http import require_GET

@require_GET
def check_staged_transaction(request):
    count = StagedTransaction.objects.count()
    return JsonResponse({'count': count})

@require_GET
def check_transaction(request):
    count = Transaction.objects.count()
    return JsonResponse({'count': count})

from .models import DailyInfo

def daily_info_view(request):
    infos = DailyInfo.objects.order_by('-transaction_date')[:30]
    return render(request, 'admin/daily_info.html', {'infos': infos})

from .models import Transaction, DailyInfo
from django.db.models import Sum, Min, Max, F
from django.shortcuts import render, redirect
from django.http import JsonResponse

def process_daily_info(request):
    # فعال/غیرفعال بودن پردازش خودکار
    auto_process = request.GET.get('auto', 'on') == 'on'
    manual = request.GET.get('manual', None)
    # آخرین تاریخ پردازش شده
    last_processed = DailyInfo.objects.order_by('-transaction_date').first()
    last_date = last_processed.transaction_date if last_processed else None
    # همه تاریخ‌های موجود در Transaction که هنوز پردازش نشده‌اند
    dates = Transaction.objects.values_list('transaction_date', flat=True).distinct()
    to_process = [d for d in dates if not DailyInfo.objects.filter(transaction_date=d).exists()]
    processed_count = DailyInfo.objects.count()
    to_process_count = len(to_process)
    # پردازش خودکار یا دستی
    if auto_process or manual:
        for date in to_process:
            txs = Transaction.objects.filter(transaction_date=date)
            total_volume = txs.aggregate(Sum('contract_volume'))['contract_volume__sum'] or 0
            total_demand = txs.aggregate(Sum('demand_volume'))['demand_volume__sum'] or 0
            total_offer = txs.aggregate(Sum('offer_volume'))['offer_volume__sum'] or 0
            total_value = txs.aggregate(Sum('transaction_value'))['transaction_value__sum'] or 0
            weighted_avg = 0
            sum_price_volume = txs.aggregate(total=Sum(F('final_price') * F('contract_volume')))['total'] or 0
            if total_volume:
                weighted_avg = round(sum_price_volume / total_volume, 2)
            final_price = txs.order_by('-id').first().final_price if txs.exists() else ''
            lowest_price = txs.aggregate(Min('final_price'))['final_price__min'] or ''
            highest_price = txs.aggregate(Max('final_price'))['final_price__max'] or ''
            # محدوده هفتگی و ۳۰ روزه
            week_dates = Transaction.objects.filter(transaction_date__lte=date).order_by('-transaction_date').values_list('transaction_date', flat=True)[:7]
            week_prices = Transaction.objects.filter(transaction_date__in=week_dates).values_list('final_price', flat=True)
            week_min = min(week_prices) if week_prices else ''
            week_max = max(week_prices) if week_prices else ''
            month_dates = Transaction.objects.filter(transaction_date__lte=date).order_by('-transaction_date').values_list('transaction_date', flat=True)[:30]
            month_prices = Transaction.objects.filter(transaction_date__in=month_dates).values_list('final_price', flat=True)
            month_min = min(month_prices) if month_prices else ''
            month_max = max(month_prices) if month_prices else ''
            monthly_change = ''
            if len(month_prices) >= 2:
                try:
                    monthly_change = round(((final_price - month_prices[-1]) / month_prices[-1]) * 100, 2)
                except:
                    monthly_change = ''
            base_price = txs.first().base_price if txs.exists() else ''
            settlement_type = txs.first().settlement_type if txs.exists() else ''
            DailyInfo.objects.create(
                avg_final_price=weighted_avg,
                final_price=final_price,
                lowest_price=lowest_price,
                highest_price=highest_price,
                weekly_range=f"{week_min}-{week_max}",
                monthly_range=f"{month_min}-{month_max}",
                monthly_change=monthly_change,
                settlement_type=settlement_type,
                transaction_date=date,
                contract_volume=total_volume,
                demand=total_demand,
                offer_volume=total_offer,
                base_price=base_price,
                transaction_value=total_value
            )
    infos = DailyInfo.objects.order_by('-transaction_date')[:30]
    return render(request, 'admin/daily_info.html', {
        'infos': infos,
        'auto_process': auto_process,
        'processed_count': processed_count,
        'to_process_count': to_process_count
    })
