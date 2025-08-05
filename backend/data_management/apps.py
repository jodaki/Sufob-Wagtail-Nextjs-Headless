from django.apps import AppConfig


class DataManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_management'
    verbose_name = '🧩 مدیریت داده‌ها'
    verbose_name_plural = '🧩 مدیریت داده‌ها'
    
    def ready(self):
        """تنظیمات اولیه اپلیکیشن"""
        pass
