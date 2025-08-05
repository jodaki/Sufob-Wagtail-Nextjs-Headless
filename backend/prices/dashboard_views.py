"""
Dashboard و Views سفارشی برای Scroll Time در Wagtail Admin
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.http import JsonResponse
from wagtail.admin import messages
from .models import ScrollTimeRequest, MainCategory, Category, SubCategory, PriceData
from .forms import ScrollTimeRequestForm


@staff_member_required
def scroll_time_dashboard(request):
    """داشبورد اصلی Scroll Time"""
    # آمار کلی
    total_requests = ScrollTimeRequest.objects.count()
    completed_requests = ScrollTimeRequest.objects.filter(status='completed').count()
    pending_requests = ScrollTimeRequest.objects.filter(status='pending').count()
    failed_requests = ScrollTimeRequest.objects.filter(status='failed').count()
    
    # آخرین درخواست‌ها
    recent_requests = ScrollTimeRequest.objects.order_by('-created_at')[:10]
    
    # آمار داده‌های قیمت
    total_price_records = PriceData.objects.count()
    
    context = {
        'page_title': 'داشبورد Scroll Time',
        'stats': {
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'pending_requests': pending_requests,
            'failed_requests': failed_requests,
            'total_price_records': total_price_records,
        },
        'recent_requests': recent_requests,
    }
    
    return render(request, 'wagtailadmin/scroll_time/dashboard.html', context)


@staff_member_required
def scroll_time_quick_create(request):
    """ایجاد سریع درخواست Scroll Time"""
    if request.method == 'POST':
        form = ScrollTimeRequestForm(request.POST)
        if form.is_valid():
            scroll_request = form.save(commit=False)
            scroll_request.created_by = str(request.user) if request.user.is_authenticated else 'ناشناس'
            scroll_request.save()
            
            messages.success(request, f'درخواست Scroll Time #{scroll_request.id} با موفقیت ایجاد شد')
            return redirect(f'/sufobadmin/scroll-time/{scroll_request.id}/send/')  # ریدایرکت به مرحله ارسال
        else:
            messages.error(request, 'خطا در ایجاد درخواست. لطفاً اطلاعات را بررسی کنید.')
    else:
        form = ScrollTimeRequestForm()
    
    # داده‌های مورد نیاز برای فرم
    main_categories = MainCategory.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'page_title': 'ایجاد درخواست Scroll Time جدید',
        'form': form,
        'main_categories': main_categories,
    }
    
    return render(request, 'wagtailadmin/scroll_time/quick_create.html', context)
