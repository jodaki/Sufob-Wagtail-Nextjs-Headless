"""
Views مربوط به Scroll Time برای Wagtail Admin
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy, reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
import json
import logging

from .models import ScrollTimeRequest, MainCategory, Category, SubCategory
from .forms import ScrollTimeRequestForm
from .services import ScrollTimeService, DataPreviewService

logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name='dispatch')
class ScrollTimeCreateView(CreateView):
    """ویو ایجاد درخواست Scroll Time"""
    model = ScrollTimeRequest
    form_class = ScrollTimeRequestForm
    template_name = 'wagtailadmin/scroll_time/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = "ایجاد درخواست Scroll Time جدید"
        context['page_subtitle'] = "دریافت داده از سازمان بورس"
        return context
    
    def get_success_url(self):
        return reverse('prices:scroll_time_send', kwargs={'pk': self.object.pk})
        return context
    
    def form_valid(self, form):
        # ذخیره created_by
        scroll_request = form.save(commit=False)
        scroll_request.created_by = str(self.request.user) if self.request.user.is_authenticated else 'ناشناس'
        scroll_request.save()
        
        messages.success(self.request, 'درخواست Scroll Time با موفقیت ایجاد شد')
        
        # هدایت به صفحه ارسال درخواست
        return redirect('prices:scroll_time_send', scroll_request.id)


class ScrollTimeSendView(DetailView):
    """ویو ارسال درخواست و پیش‌نمایش نتایج"""
    model = ScrollTimeRequest
    template_name = 'wagtailadmin/scroll_time/send.html'
    context_object_name = 'scroll_request'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'ارسال درخواست Scroll Time'
        context['page_subtitle'] = f'درخواست #{self.object.id}'
        return context
    
    def post(self, request, *args, **kwargs):
        """ارسال درخواست به سرور بورس"""
        import json
        import traceback
        from django.utils import timezone
        
        scroll_request = self.get_object()
        action = request.POST.get('action', 'send_request')
        
        # لاگ درخواست
        debug_info = {
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'request_id': scroll_request.id,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'method': request.method,
            'csrf_token': request.POST.get('csrfmiddlewaretoken', 'Missing')[:10] + '...',
        }
        
        if action == 'test':
            messages.success(request, f'✅ تست ارتباط موفق! اطلاعات: {json.dumps(debug_info, indent=2)}')
            return self.get(request, *args, **kwargs)
        
        if scroll_request.status not in ['pending', 'failed']:
            messages.warning(request, 'این درخواست قبلاً پردازش شده است')
            return redirect('prices:scroll_time_preview', scroll_request.id)

        try:
            # ارسال درخواست
            service = ScrollTimeService()
            result = service.fetch_data(scroll_request)
            
            # بررسی نتیجه و نمایش اطلاعات کامل برای debug
            if result['success']:
                debug_info['result'] = 'SUCCESS'
                debug_info['records_count'] = len(result.get('data', []))
                messages.success(request, f"✅ {result['message']}")
                messages.info(request, f"Debug Info: {json.dumps(debug_info, indent=2)}")
                return redirect('prices:scroll_time_preview', scroll_request.id)
            else:
                debug_info['result'] = 'FAILED'
                debug_info['error'] = result.get('error', 'Unknown error')
                
                # اطلاعات کامل برای debug
                full_debug = f"""
                ❌ خطا در ارسال درخواست:
                
                🔗 URL: {service.BASE_URL}
                
                📝 Payload ارسالی:
                {scroll_request.get_payload()}
                
                ⚠️ خطای دریافت شده:
                {result.get('error', 'خطای ناشناخته')}
                
                📊 وضعیت درخواست: {scroll_request.status}
                
                🔧 Headers استفاده شده:
                {service.DEFAULT_HEADERS}
                
                🐛 Debug Info:
                {json.dumps(debug_info, indent=2, ensure_ascii=False)}
                """
                
                # نمایش پیام خطا به کاربر
                messages.error(request, f"خطا در ارسال درخواست: {result['error']}")
                messages.warning(request, full_debug)
                
                # لاگ کردن اطلاعات کامل برای مطالعه
                logger.error(f"API Call Failed - Debug Info: {full_debug}")
                
                # افزودن اطلاعات debug به context برای نمایش در template
                context = self.get_context_data()
                context['debug_info'] = full_debug
                context['api_error'] = True
                
                return self.render_to_response(context)
                
        except Exception as e:
            debug_info['result'] = 'EXCEPTION'
            debug_info['exception'] = str(e)
            debug_info['traceback'] = traceback.format_exc()
            
            error_msg = f"خطای سیستمی: {str(e)}"
            messages.error(request, error_msg)
            messages.error(request, f"Debug Info: {json.dumps(debug_info, indent=2, ensure_ascii=False)}")
            
            logger.error(f"System Error in ScrollTimeSendView: {traceback.format_exc()}")
            
            return self.get(request, *args, **kwargs)


class ScrollTimePreviewView(DetailView):
    """ویو پیش‌نمایش داده‌های دریافت شده"""
    model = ScrollTimeRequest
    template_name = 'wagtailadmin/scroll_time/preview.html'
    context_object_name = 'scroll_request'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # دریافت داده‌های پیش‌نمایش
        preview_service = DataPreviewService()
        preview_result = preview_service.get_preview_data(self.object, limit=5)
        
        context.update({
            'page_title': 'پیش‌نمایش داده‌های دریافت شده',
            'page_subtitle': f'درخواست #{self.object.id}',
            'preview_data': preview_result,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        """ذخیره داده‌ها در پایگاه داده"""
        import json
        import traceback
        from django.utils import timezone
        
        scroll_request = self.get_object()
        action = request.POST.get('action')
        
        # لاگ درخواست
        debug_info = {
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'request_id': scroll_request.id,
            'status': scroll_request.status,
            'has_response_data': bool(scroll_request.response_data),
            'response_data_length': len(scroll_request.response_data) if scroll_request.response_data else 0,
        }
        
        if action == 'test_save':
            messages.info(request, f'🧪 تست ذخیره - اطلاعات درخواست: {json.dumps(debug_info, indent=2, ensure_ascii=False)}')
            return self.get(request, *args, **kwargs)
        
        if action == 'save':
            try:
                service = ScrollTimeService()
                result = service.save_data_to_database(scroll_request)
                
                debug_info['save_result'] = result.get('success', False)
                debug_info['save_stats'] = result.get('stats', {})
                
                if result['success']:
                    messages.success(request, f"✅ {result['message']}")
                    messages.info(request, f"📊 آمار عملیات: {json.dumps(result.get('stats', {}), indent=2, ensure_ascii=False)}")
                    return redirect('prices:scroll_time_completed', scroll_request.id)
                else:
                    debug_info['error'] = result.get('error', 'Unknown error')
                    messages.error(request, f"❌ خطا در ذخیره: {result['error']}")
                    messages.warning(request, f"🐛 Debug Info: {json.dumps(debug_info, indent=2, ensure_ascii=False)}")
                    
            except Exception as e:
                debug_info['exception'] = str(e)
                debug_info['traceback'] = traceback.format_exc()
                
                error_msg = f"خطای سیستمی در ذخیره داده‌ها: {str(e)}"
                messages.error(request, error_msg)
                messages.error(request, f"🐛 Debug Info: {json.dumps(debug_info, indent=2, ensure_ascii=False)}")
                
                logger.error(f"System Error in ScrollTimePreviewView save: {traceback.format_exc()}")
                
        elif action == 'cancel':
            scroll_request.status = 'pending'
            scroll_request.response_data = None
            scroll_request.save()
            messages.info(request, 'عملیات لغو شد')
            return redirect('prices:scroll_time_create')
        
        return self.get(request, *args, **kwargs)


class ScrollTimeCompletedView(DetailView):
    """ویو نمایش گزارش نهایی"""
    model = ScrollTimeRequest
    template_name = 'wagtailadmin/scroll_time/completed.html'
    context_object_name = 'scroll_request'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'گزارش نهایی Scroll Time',
            'page_subtitle': f'درخواست #{self.object.id}',
        })
        return context


# AJAX Views برای بروزرسانی فرم‌ها
@csrf_exempt
def ajax_get_categories(request):
    """دریافت گروه‌ها براساس گروه اصلی"""
    if request.method == 'GET':
        main_category_id = request.GET.get('main_category') or request.GET.get('main_category_id')
        
        if main_category_id:
            categories = Category.objects.filter(
                main_category_id=main_category_id,
                is_active=True
            ).values('id', 'name', 'value')
            
            return JsonResponse({
                'success': True,
                'categories': list(categories)
            })
    
    return JsonResponse({'success': False, 'categories': []})


@csrf_exempt
def ajax_get_subcategories(request):
    """دریافت زیرگروه‌ها براساس گروه"""
    if request.method == 'GET':
        category_id = request.GET.get('category') or request.GET.get('category_id')
        
        if category_id:
            subcategories = SubCategory.objects.filter(
                category_id=category_id,
                is_active=True
            ).values('id', 'name', 'value')
            
            return JsonResponse({
                'success': True,
                'subcategories': list(subcategories)
            })
    
    return JsonResponse({'success': False, 'subcategories': []})


@csrf_exempt 
def ajax_scroll_time_status(request):
    """بررسی وضعیت درخواست Scroll Time"""
    if request.method == 'GET':
        request_id = request.GET.get('request_id')
        
        if request_id:
            scroll_request = get_object_or_404(ScrollTimeRequest, id=request_id)
            
            return JsonResponse({
                'success': True,
                'status': scroll_request.status,
                'total_records': scroll_request.total_records,
                'processed_records': scroll_request.processed_records,
                'error_message': scroll_request.error_message,
            })
    
    return JsonResponse({'success': False})
