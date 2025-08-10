#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sufob.settings.dev')
django.setup()

from data_management.models import AllData

print("=== بررسی داده‌های AllData ===")
print(f"تعداد کل رکوردها: {AllData.objects.count()}")

print("\n=== نام کالاهای موجود ===")
commodity_names = AllData.objects.values_list('commodity_name', flat=True).distinct()
for name in commodity_names[:20]:
    if name:
        print(f"- {name}")
    else:
        print("- (خالی)")

print(f"\nتعداد کل commodity_name های منحصر به فرد: {len(set(commodity_names))}")

print("\n=== نمونه رکورد ===")
sample = AllData.objects.first()
if sample:
    print(f"ID: {sample.id}")
    print(f"Commodity Name: {sample.commodity_name}")
    print(f"Final Price: {sample.final_price}")
    print(f"Transaction Date: {sample.transaction_date}")
    print(f"Symbol: {sample.symbol}")
