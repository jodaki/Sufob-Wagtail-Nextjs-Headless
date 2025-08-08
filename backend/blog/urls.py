from django.urls import path
from .views import scroll_time_save_data

urlpatterns = [
    path('save-scroll-time-data/<int:page_id>/', scroll_time_save_data, name='save_scroll_time_data'),
]
