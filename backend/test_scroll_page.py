#!/usr/bin/env python
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sufob.settings.development')
django.setup()

from blog.models import ScrollTimePage
from data_management.models import AllData

def test_save_functionality():
    try:
        # دریافت ScrollTimePage که ایجاد کردیم
        scroll_page = ScrollTimePage.objects.get(id=16)
        print(f"📄 ScrollTimePage found: {scroll_page.title}")
        print(f"🔗 API URL: {scroll_page.api_url}")
        
        # تست متد save_data_from_api
        print("\n🔄 Testing save_data_from_api method...")
        result = scroll_page.save_data_from_api()
        
        print(f"✅ Method result: {result}")
        
        # بررسی داده‌ها در AllData
        all_data_count = AllData.objects.count()
        print(f"📊 Total records in AllData: {all_data_count}")
        
        # نمایش آخرین رکوردها
        latest_records = AllData.objects.order_by('-id')[:5]
        for record in latest_records:
            print(f"   - {record.symbol} ({record.isin}): {record.final_price}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_functionality()
