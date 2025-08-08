from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http import JsonResponse
from price_models.models import PriceData, DataImportLog

# Create your views here.

@method_decorator(staff_member_required, name='dispatch')
class PriceDataImportView(TemplateView):
    template_name = 'admin/prices/import_data.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'وارد کردن داده‌های قیمت',
            'recent_imports': DataImportLog.objects.all()[:10],
            'total_price_records': PriceData.objects.count(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        # Handle file upload and import logic here
        if 'import_file' in request.FILES:
            # Add your import logic here
            messages.success(request, 'فایل با موفقیت آپلود شد!')
            return redirect('price_data_import')
        
        messages.error(request, 'فایلی انتخاب نشده است!')
        return self.get(request, *args, **kwargs)
