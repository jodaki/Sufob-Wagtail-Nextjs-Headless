from django.urls import path
from . import views

app_name = 'data_management'

urlpatterns = [
    path('', views.data_summary_view, name='summary'),
    path('all-records/', views.all_data_list_view, name='all_records'),
    path('daily/', views.daily_data_list_view, name='daily'),
    path('weekly/', views.weekly_data_list_view, name='weekly'),
    path('monthly/', views.monthly_data_list_view, name='monthly'),
    path('yearly/', views.yearly_data_list_view, name='yearly'),
]
