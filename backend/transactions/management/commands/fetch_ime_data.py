import json
import logging
import csv
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from transactions.models import Transaction
import requests

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'استخراج معاملات کنسانتره سنگ آهن از سایت بورس کالا و ذخیره در دیتابیس'

    def handle(self, *args, **options):
        from_date = "1404/04/01"
        to_date = "1404/04/29"
        main_cat = 1
        cat = 49
        sub_cat = 477
        start_time = datetime.now()
        self.stdout.write(self.style.NOTICE(f"شروع استخراج داده‌ها از {from_date} تا {to_date}"))

        url = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList"
        payload = {
            "Language": 8,
            "fari": False,
            "GregorianFromDate": from_date,
            "GregorianToDate": to_date,
            "MainCat": main_cat,
            "Cat": cat,
            "SubCat": sub_cat,
            "Producer": 0
        }
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "text/plain, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept-Language": "fa-IR,fa;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6"
        }

        total_records = 0
        new_records = 0
        duplicate_records = 0
        error_records = []

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        data_csv = output_dir / "ime_data.csv"
        error_csv = output_dir / "ime_errors.csv"

        csv_headers = [
            "GoodsName", "Symbol", "Talar", "ProducerName", "ContractType",
            "Price", "TotalPrice", "MinPrice", "MaxPrice", "ArzeBasePrice",
            "arze", "taghaza", "Quantity", "Unit", "date", "ArzehKonandeh",
            "cBrokerSpcName", "Tasvieh", "DeliveryDate", "Warehouse",
            "SettlementDate", "xTalarReportPK", "bArzehRadifTarSarresid",
            "ModeDescription", "MethodDescription", "Currency", "PacketName", "arzehPk"
        ]

        if not data_csv.exists():
            with open(data_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_headers)
                writer.writeheader()
        if not error_csv.exists():
            with open(error_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_headers + ["دلیل خطا"])
                writer.writeheader()

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = json.loads(response.json().get("d", "[]"))
            total_records = len(data)
            self.stdout.write(self.style.SUCCESS(f"[DEBUG] تعداد داده دریافتی از API: {total_records}"))
            if total_records > 0:
                self.stdout.write(self.style.HTTP_INFO(f"[DEBUG] نمونه داده دریافتی:\n{json.dumps(data[0], ensure_ascii=False, indent=2)}"))
            for item in data:
                required_fields = ["GoodsName", "Symbol", "date", "ArzeBasePrice"]
                missing_fields = [field for field in required_fields if not item.get(field)]
                if missing_fields:
                    # فقط فیلدهای مجاز + دلیل خطا را ذخیره کن
                    filtered_error = {k: item.get(k, None) for k in csv_headers}
                    filtered_error["دلیل خطا"] = f"فیلدهای ناقص: {', '.join(missing_fields)}"
                    error_records.append(filtered_error)
                    continue
                x_talar_report_pk = item.get("xTalarReportPK")
                if Transaction.objects.filter(x_talar_report_pk=x_talar_report_pk).exists():
                    duplicate_records += 1
                    continue
                try:
                    Transaction.objects.create(
                        commodity_name=item["GoodsName"],
                        symbol=item["Symbol"],
                        hall=item["Talar"],
                        producer=item["ProducerName"],
                        contract_type=item["ContractType"],
                        final_price=float(item["Price"]) if item["Price"] else None,
                        transaction_value=int(item["TotalPrice"]) if item["TotalPrice"] else 0,
                        lowest_price=float(item["MinPrice"]) if item["MinPrice"] else None,
                        highest_price=float(item["MaxPrice"]) if item["MaxPrice"] else None,
                        base_price=float(item["ArzeBasePrice"]),
                        offer_volume=int(item["arze"]),
                        demand_volume=int(item["taghaza"]),
                        contract_volume=int(item["Quantity"]),
                        unit=item["Unit"],
                        transaction_date=item["date"],
                        supplier=item["ArzehKonandeh"],
                        broker=item["cBrokerSpcName"],
                        settlement_type=item["Tasvieh"],
                        delivery_date=item["DeliveryDate"],
                        warehouse=item["Warehouse"],
                        settlement_date=item["SettlementDate"],
                        x_talar_report_pk=int(item["xTalarReportPK"]) if item["xTalarReportPK"] else None,
                        b_arzeh_radif_tar_sarresid=item["bArzehRadifTarSarresid"],
                        mode_description=item["ModeDescription"],
                        method_description=item["MethodDescription"],
                        currency=item["Currency"],
                        packet_name=item["PacketName"],
                        arzeh_pk=int(item["arzehPk"]) if item["arzehPk"] else None
                    )
                    # فقط فیلدهای مجاز را در CSV ذخیره کن
                    filtered_item = {k: item.get(k, None) for k in csv_headers}
                    with open(data_csv, mode='a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=csv_headers)
                        writer.writerow(filtered_item)
                    new_records += 1
                except (ValueError, IntegrityError) as e:
                    filtered_error = {k: item.get(k, None) for k in csv_headers}
                    filtered_error["دلیل خطا"] = str(e)
                    error_records.append(filtered_error)
        except requests.RequestException as e:
            error_records.append({"دلیل خطا": f"خطای اتصال: {str(e)}"})
            self.stdout.write(self.style.ERROR(f"خطا در اتصال به API: {e}"))
        finally:
            if error_records:
                with open(error_csv, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=csv_headers + ["دلیل خطا"])
                    writer.writerows(error_records)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(self.style.SUCCESS(f"\nگزارش استخراج داده‌ها:"))
            self.stdout.write(f"- زمان شروع: {start_time}")
            self.stdout.write(f"- زمان پایان: {end_time}")
            self.stdout.write(f"- مدت زمان اجرا: {duration:.2f} ثانیه")
            self.stdout.write(f"- تعداد کل رکوردها: {total_records}")
            self.stdout.write(f"- تعداد رکوردهای جدید: {new_records}")
            self.stdout.write(f"- تعداد رکوردهای تکراری: {duplicate_records}")
            self.stdout.write(f"- تعداد رکوردهای دارای خطا: {len(error_records)}")
