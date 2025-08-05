from django.urls import path
from django.http import JsonResponse
from .views import PriceDataImportView
from .scroll_time_views import (
    ScrollTimeCreateView,
    ScrollTimeSendView,
    ScrollTimePreviewView,
    ScrollTimeCompletedView,
    ajax_get_categories,
    ajax_get_subcategories,
)

app_name = 'prices'

urlpatterns = [
    # درخواست‌های موجود
    path('import/', PriceDataImportView.as_view(), name='price_data_import'),
    
    # Scroll Time URLs
    path('scroll-time/create/', ScrollTimeCreateView.as_view(), name='scroll_time_create'),
    path('scroll-time/<int:pk>/send/', ScrollTimeSendView.as_view(), name='scroll_time_send'),
    path('scroll-time/<int:pk>/preview/', ScrollTimePreviewView.as_view(), name='scroll_time_preview'),
    path('scroll-time/<int:pk>/completed/', ScrollTimeCompletedView.as_view(), name='scroll_time_completed'),
    
    # AJAX URLs
    path('ajax/categories/', ajax_get_categories, name='ajax_get_categories'),
    path('ajax/subcategories/', ajax_get_subcategories, name='ajax_get_subcategories'),
    path('ajax/scroll-time-status/', lambda request: JsonResponse({'success': False, 'error': 'Not implemented'}), name='ajax_scroll_time_status'),
]
