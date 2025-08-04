import requests
import json
import logging
import csv
from datetime import datetime
from pathlib import Path
from django.db import IntegrityError
from transactions.models import StagedTransaction
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ime_project.settings")
django.setup()

import requests
import json
import logging
import csv
from datetime import datetime
from pathlib import Path
from django.db import IntegrityError
from transactions.models import Transaction

# بقیه کد (همون کد قبلی)
# تنظیم لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ime_data_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_ime_data(from_date="1404/04/01", to_date="1404/04/29", main_cat=1, cat=49, sub_cat=477):
    """
    استخراج داده‌های معاملات کنسانتره سنگ آهن از API IME و ذخیره در دیتابیس و CSV
    """
    start_time = datetime.now()
    logger.info(f"شروع استخراج داده‌ها از {from_date} تا {to_date}")

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

    # متغیرهای شمارشگر
    total_records = 0
    staged_records = 0
    error_records = []

    # مسیر فایل‌های CSV
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    data_csv = output_dir / "ime_data.csv"
    error_csv = output_dir / "ime_errors.csv"

    # هدرهای CSV
    csv_headers = [
        "GoodsName", "Symbol", "Talar", "ProducerName", "ContractType",
        "Price", "TotalPrice", "MinPrice", "MaxPrice", "ArzeBasePrice",
        "arze", "taghaza", "Quantity", "Unit", "date", "ArzehKonandeh",
        "cBrokerSpcName", "Tasvieh", "DeliveryDate", "Warehouse",
        "SettlementDate", "xTalarReportPK", "bArzehRadifTarSarresid",
        "ModeDescription", "MethodDescription", "Currency", "PacketName", "arzehPk"
    ]

    # نوشتن هدر در فایل CSV داده‌ها
    if not data_csv.exists():
        with open(data_csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()

    # نوشتن هدر در فایل CSV خطاها
    if not error_csv.exists():
        with open(error_csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers + ["دلیل خطا"])
            writer.writeheader()

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()  # خطا در صورت پاسخ غیر 200
        data = json.loads(response.json().get("d", "[]"))
        total_records = len(data)

        print(f"\n\033[92m[DEBUG] تعداد داده دریافتی از API: {total_records}\033[0m\n")
        if total_records > 0:
            print(f"\033[94m[DEBUG] نمونه داده دریافتی:\033[0m\n{json.dumps(data[0], ensure_ascii=False, indent=2)}\n")

        for item in data:
            # بررسی فیلدهای اجباری
            required_fields = ["GoodsName", "Symbol", "date", "ArzeBasePrice"]
            missing_fields = [field for field in required_fields if not item.get(field)]
            if missing_fields:
                error_records.append({
                    **item,
                    "دلیل خطا": f"فیلدهای ناقص: {', '.join(missing_fields)}"
                })
                logger.warning(f"رکورد ناقص: {item.get('Symbol')} - فیلدهای ناقص: {missing_fields}")
                continue

            try:
                StagedTransaction.objects.create(
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
                # ذخیره در CSV
                with open(data_csv, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=csv_headers)
                    writer.writerow(item)
                staged_records += 1
                logger.info(f"رکورد موقت ذخیره شد: {item['Symbol']} - {item['date']}")
            except (ValueError, IntegrityError) as e:
                error_records.append({
                    **item,
                    "دلیل خطا": str(e)
                })
                logger.error(f"خطا در ذخیره رکورد موقت {item['Symbol']} - {item['date']}: {e}")

    except requests.RequestException as e:
        logger.error(f"خطا در اتصال به API: {e}")
        error_records.append({"دلیل خطا": f"خطای اتصال: {str(e)}"})

    finally:
        # ذخیره خطاها در CSV
        if error_records:
            with open(error_csv, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=csv_headers + ["دلیل خطا"])
                writer.writerows(error_records)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # گزارش نهایی
        logger.info(f"""
        گزارش استخراج داده‌ها:
        - زمان شروع: {start_time}
        - زمان پایان: {end_time}
        - مدت زمان اجرا: {duration:.2f} ثانیه
        - تعداد کل رکوردها: {total_records}
        - تعداد رکوردهای موقت ذخیره شده: {staged_records}
        - تعداد رکوردهای دارای خطا: {len(error_records)}
        """)

if __name__ == "__main__":
    fetch_ime_data()