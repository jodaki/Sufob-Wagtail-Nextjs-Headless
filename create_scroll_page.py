#!/usr/bin/env python
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sufob.settings.development')
django.setup()

from blog.models import ScrollTimePage
from home.models import HomePage

def create_scroll_page():
    try:
        # دریافت صفحه home برای والد
        home_page = HomePage.objects.first()
        print(f"Home page found: {home_page}")
        
        if not home_page:
            print("❌ No HomePage found!")
            return
        
        # بررسی اینکه آیا ScrollTimePage قبلاً وجود دارد
        existing = ScrollTimePage.objects.filter(title="تست داده‌های بورس").first()
        if existing:
            print(f"✅ ScrollTimePage already exists with ID: {existing.id}")
            return existing.id
        
        # ایجاد ScrollTimePage جدید
        scroll_page = ScrollTimePage(
            title="تست داده‌های بورس",
            slug="test-bourse-data",
            api_url="https://old.tsetmc.com/tsev2/data/TseClient2.aspx?t=LastPossibleDeven"
        )
        
        # اضافه کردن به home page
        home_page.add_child(instance=scroll_page)
        scroll_page.save_revision().publish()
        
        print(f"✅ ScrollTimePage created successfully!")
        print(f"   ID: {scroll_page.id}")
        print(f"   Title: {scroll_page.title}")
        print(f"   API URL: {scroll_page.api_url}")
        print(f"   Admin URL: http://localhost:8001/sufobadmin/pages/{scroll_page.id}/edit/")
        
        return scroll_page.id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_scroll_page()
