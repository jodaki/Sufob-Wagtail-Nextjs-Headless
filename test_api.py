#!/usr/bin/env python
import os
import sys
import django
import requests

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sufob.settings.development')
django.setup()

def test_api():
    try:
        url = "https://old.tsetmc.com/tsev2/data/TseClient2.aspx?t=LastPossibleDeven"
        print(f"🔗 Testing API: {url}")
        
        response = requests.get(url)
        response.raise_for_status()
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Content Type: {response.headers.get('content-type', 'unknown')}")
        print(f"📄 Response Length: {len(response.text)} characters")
        print(f"🔢 Response Preview: {response.text[:200]}...")
        
        # تلاش برای تجزیه JSON
        try:
            json_data = response.json()
            print(f"✅ JSON Parse Success: {type(json_data)}")
            if isinstance(json_data, list):
                print(f"📋 Array Length: {len(json_data)}")
                if len(json_data) > 0:
                    print(f"🔍 First Item: {json_data[0]}")
        except Exception as e:
            print(f"❌ JSON Parse Failed: {e}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
