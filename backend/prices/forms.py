from django import forms
from django.core.exceptions import ValidationError
from .models import PriceData
from datetime import date, timedelta

class DataImportForm(forms.Form):
    """فرم وارد کردن داده‌های قیمت"""
    
    COMMODITY_CHOICES = [
        ('کنسانتره آهن', 'کنسانتره آهن'),
        ('سنگ آهن', 'سنگ آهن'),
        ('کاتد مس', 'کاتد مس'),
        ('شمش آلومینیوم', 'شمش آلومینیوم'),
        ('کک متالورژی', 'کک متالورژی'),
        ('طلا', 'طلا'),
        ('نقره', 'نقره'),
        ('مس', 'مس'),
        ('آلومینیوم', 'آلومینیوم'),
        ('روی', 'روی'),
    ]
    
    DUPLICATE_HANDLING_CHOICES = [
        ('skip', 'رد کردن رکوردهای تکراری'),
        ('replace', 'جایگزینی رکوردهای تکراری'),
        ('update', 'بروزرسانی رکوردهای موجود'),
    ]
    
    commodity_name = forms.ChoiceField(
        choices=COMMODITY_CHOICES,
        label="نوع محصول",
        help_text="نوع کالا را انتخاب کنید",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        label="تاریخ شروع",
        help_text="تاریخ شروع بازه زمانی داده‌ها",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=lambda: date.today() - timedelta(days=30)
    )
    
    end_date = forms.DateField(
        label="تاریخ پایان", 
        help_text="تاریخ پایان بازه زمانی داده‌ها",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=date.today
    )
    
    duplicate_handling = forms.ChoiceField(
        choices=DUPLICATE_HANDLING_CHOICES,
        label="نحوه مواجهه با داده‌های تکراری",
        help_text="تعیین کنید در صورت وجود داده تکراری چه کار شود",
        widget=forms.RadioSelect,
        initial='skip'
    )
    
    auto_save = forms.BooleanField(
        label="ذخیره خودکار در پایگاه داده",
        help_text="در صورت فعال بودن، داده‌ها بلافاصله ذخیره می‌شوند",
        required=False,
        initial=True
    )
    
    fetch_from_api = forms.BooleanField(
        label="دریافت از API بورس کالا",
        help_text="دریافت داده‌ها از API رسمی بورس کالای ایران",
        required=False,
        initial=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('تاریخ شروع نمی‌تواند بعد از تاریخ پایان باشد.')
            
            if end_date > date.today():
                raise ValidationError('تاریخ پایان نمی‌تواند در آینده باشد.')
            
            # محدودیت بازه زمانی (مثلاً حداکثر 1 سال)
            if (end_date - start_date).days > 365:
                raise ValidationError('بازه زمانی نمی‌تواند بیش از یک سال باشد.')
        
        return cleaned_data


class PriceDataExportForm(forms.Form):
    """فرم خروجی گرفتن از داده‌های قیمت"""
    
    EXPORT_FORMAT_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV (.csv)'),
        ('json', 'JSON (.json)'),
    ]
    
    commodity_names = forms.MultipleChoiceField(
        choices=PriceData.COMMODITY_CHOICES,
        label="کالاهای انتخابی",
        help_text="کالاهایی که می‌خواهید خروجی بگیرید",
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    start_date = forms.DateField(
        label="از تاریخ",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    
    end_date = forms.DateField(
        label="تا تاریخ",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    
    export_format = forms.ChoiceField(
        choices=EXPORT_FORMAT_CHOICES,
        label="فرمت خروجی",
        initial='excel',
        widget=forms.RadioSelect
    )
    
    include_statistics = forms.BooleanField(
        label="شامل آمار خلاصه",
        help_text="افزودن آمار کلی به خروجی",
        required=False,
        initial=False
    )
