#!/usr/bin/env python
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sufob.settings.development')
django.setup()

from blog.models import ScrollTimePage

def simple_test():
    try:
        # دریافت ScrollTimePage
        scroll_page = ScrollTimePage.objects.get(id=16)
        print(f"📄 ScrollTimePage: {scroll_page.title}")
        print(f"🔗 API URL: {scroll_page.api_url}")
        
        # تست متد save_data_from_api
        print("\n🔄 Testing API...")
        result = scroll_page.save_data_from_api()
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
