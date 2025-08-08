from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import ScrollTimePage


def scroll_time_save_data(request, page_id):
    """ذخیره داده‌های scroll-time از API"""
    page = get_object_or_404(ScrollTimePage, id=page_id)
    
    if request.method == 'POST':
        try:
            success, message = page.save_data_from_api()
            
            if success:
                # Update the last fetch time and count
                from django.utils import timezone
                page.last_fetch_time = timezone.now()
                # The count will be included in the message
                try:
                    # استخراج تعداد رکوردها از پیام
                    import re
                    count_match = re.search(r'تعداد (\d+) رکورد', message)
                    if count_match:
                        page.last_fetch_count = int(count_match.group(1))
                except (IndexError, ValueError, AttributeError) as e:
                    # ثبت خطا در لاگ
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"خطا در استخراج تعداد رکورد: {e}")
                
                page.save(update_fields=['last_fetch_time', 'last_fetch_count'])
                messages.success(request, f"✅ {message}")
            else:
                messages.error(request, f"❌ {message}")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            messages.error(request, f"❌ خطای سیستمی: {str(e)}")
            
            # ثبت خطا در لاگ
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"خطا در ذخیره داده‌ها: {error_details}")
        
        # Redirect to preview to see the saved data
        if 'preview' in request.META.get('HTTP_REFERER', ''):
            # If we came from preview, go back there
            return redirect(request.META.get('HTTP_REFERER', ''))
        else:
            # Otherwise go to admin edit
            return redirect('wagtailadmin_pages:edit', page_id)
    
    return JsonResponse({'error': 'فقط درخواست POST مجاز است'}, status=405)

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import BlogPage, BlogPageView


@csrf_exempt
@require_POST
def update_view_count(request, blog_page_id):
    try:
        ip_address = get_client_ip(request)
        user = request.user if request.user.is_authenticated else None
        blog_page = BlogPage.objects.get(id=blog_page_id)
        blog_page.view_count += 1
        blog_page.save()
        BlogPageView.objects.create(
            blog_page=blog_page,
            ip_address=ip_address,
            user=user,
        )
        return JsonResponse({"status": "success", "view_count": blog_page.view_count})
    except BlogPage.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Blog page not found"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def health_check(request):
    return HttpResponse("OK", content_type="text/plain")
