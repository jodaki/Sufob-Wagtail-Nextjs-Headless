from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from transactions.models import StagedTransaction, Transaction
from django.db import IntegrityError, transaction as db_transaction

@csrf_exempt
@require_POST
def confirm_staged_transactions(request):
    """
    رکوردهای موقت را به Transaction منتقل می‌کند و آمار می‌دهد
    """
    staged = list(StagedTransaction.objects.all())
    success, duplicate, error = 0, 0, 0
    error_list = []
    for s in staged:
        try:
            # بررسی تکراری بودن بر اساس symbol و transaction_date
            if Transaction.objects.filter(symbol=s.symbol, transaction_date=s.transaction_date).exists():
                duplicate += 1
                continue
            with db_transaction.atomic():
                Transaction.objects.create(
                    commodity_name=s.commodity_name,
                    symbol=s.symbol,
                    hall=s.hall,
                    producer=s.producer,
                    contract_type=s.contract_type,
                    final_price=s.final_price,
                    transaction_value=s.transaction_value,
                    lowest_price=s.lowest_price,
                    highest_price=s.highest_price,
                    base_price=s.base_price,
                    offer_volume=s.offer_volume,
                    demand_volume=s.demand_volume,
                    contract_volume=s.contract_volume,
                    unit=s.unit,
                    transaction_date=s.transaction_date,
                    supplier=s.supplier,
                    broker=s.broker,
                    settlement_type=s.settlement_type,
                    delivery_date=s.delivery_date,
                    warehouse=s.warehouse,
                    settlement_date=s.settlement_date,
                    x_talar_report_pk=s.x_talar_report_pk,
                    b_arzeh_radif_tar_sarresid=s.b_arzeh_radif_tar_sarresid,
                    mode_description=s.mode_description,
                    method_description=s.method_description,
                    currency=s.currency,
                    packet_name=s.packet_name,
                    arzeh_pk=s.arzeh_pk
                )
            success += 1
        except IntegrityError as e:
            error += 1
            error_list.append(str(e))
        except Exception as e:
            error += 1
            error_list.append(str(e))

    # ثبت گزارش در ImportLog
    from transactions.models import ImportLog
    if staged:
        ImportLog.objects.create(
            product_type="iron_concentrate",  # یا مقدار دلخواه
            from_date=staged[0].transaction_date if staged else '',
            to_date=staged[-1].transaction_date if staged else '',
            record_count=len(staged),
            status="ذخیره شده" if success > 0 else "رد شد",
            add_type="دستی"
        )

    # پاک کردن رکوردهای موقت
    StagedTransaction.objects.all().delete()
    return JsonResponse({
        'success': success,
        'duplicate': duplicate,
        'error': error,
        'error_list': error_list
    })
