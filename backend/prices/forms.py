from django import forms
from django.core.exceptions import ValidationError
from price_models.models import PriceData
from price_data_ingestion.models import MainCategory, Category, SubCategory, ScrollTimeRequest
from datetime import date, timedelta
import re


class ScrollTimeRequestForm(forms.ModelForm):
    """فرم درخواست Scroll Time"""
    
    # فیلدهای تاریخ شمسی
    start_date_shamsi = forms.CharField(
        max_length=10,
        label="تاریخ شروع (شمسی)",
        help_text="فرمت: 1404/5/11",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1404/5/11',
            'pattern': r'\d{4}/\d{1,2}/\d{1,2}'
        })
    )
    
    end_date_shamsi = forms.CharField(
        max_length=10,
        label="تاریخ پایان (شمسی)",
        help_text="فرمت: 1404/5/14",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1404/5/14',
            'pattern': r'\d{4}/\d{1,2}/\d{1,2}'
        })
    )
    
    class Meta:
        model = ScrollTimeRequest
        fields = [
            'main_category', 'category', 'subcategory',
            'start_date_shamsi', 'end_date_shamsi',
            'duplicate_handling', 'auto_save'
        ]
        widgets = {
            'main_category': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'updateCategories(this.value)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'updateSubCategories(this.value)'
            }),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'duplicate_handling': forms.Select(attrs={'class': 'form-control'}),
            'auto_save': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # فیلتر کردن گزینه‌های فعال
        self.fields['main_category'].queryset = MainCategory.objects.filter(is_active=True)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['subcategory'].queryset = SubCategory.objects.filter(is_active=True)
        
        # اگر در حالت ویرایش هستیم، فیلترها را به‌روزرسانی کنیم
        if self.instance and self.instance.pk:
            if self.instance.main_category:
                self.fields['category'].queryset = Category.objects.filter(
                    main_category=self.instance.main_category, is_active=True
                )
            if self.instance.category:
                self.fields['subcategory'].queryset = SubCategory.objects.filter(
                    category=self.instance.category, is_active=True
                )
    
    def clean_start_date_shamsi(self):
        """اعتبارسنجی تاریخ شروع شمسی"""
        date_str = self.cleaned_data['start_date_shamsi']
        if not re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
            raise ValidationError('فرمت تاریخ باید به صورت 1404/5/11 باشد')
        return date_str
    
    def clean_end_date_shamsi(self):
        """اعتبارسنجی تاریخ پایان شمسی"""
        date_str = self.cleaned_data['end_date_shamsi']
        if not re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
            raise ValidationError('فرمت تاریخ باید به صورت 1404/5/14 باشد')
        return date_str
    
    def clean(self):
        """اعتبارسنجی کلی فرم"""
        cleaned_data = super().clean()
        main_category = cleaned_data.get('main_category')
        category = cleaned_data.get('category')
        subcategory = cleaned_data.get('subcategory')
        
        # بررسی ارتباط دسته‌بندی‌ها
        if category and main_category:
            if category.main_category != main_category:
                raise ValidationError('گروه انتخاب شده با گروه اصلی مطابقت ندارد')
        
        if subcategory and category:
            if subcategory.category != category:
                raise ValidationError('زیرگروه انتخاب شده با گروه مطابقت ندارد')
        
        return cleaned_data


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
