from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from wagtail import hooks
from wagtail.admin import messages
from django.urls import path, reverse
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpRequest
from django.utils.html import format_html

from .models import BlogCategory, ScrollTimePage


class BlogCategoryAdmin(ModelAdmin):
    model = BlogCategory
    menu_label = 'دسته‌بندی‌ها'
    menu_icon = 'tag'
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False

    list_display = ('name', 'slug', 'chinese_name')
    list_filter = ('name',)
    search_fields = ('name', 'slug', 'chinese_name')


modeladmin_register(BlogCategoryAdmin)


# اضافه کردن قابلیت ذخیره داده‌ها برای scroll-time
@hooks.register('register_admin_urls')
def register_scroll_time_urls():
    return [
        path('scroll-time/<int:page_id>/save-data/', save_scroll_time_data, name='save_scroll_time_data'),
    ]


def save_scroll_time_data(request: HttpRequest, page_id: int):
    """View برای ذخیره داده‌های scroll-time"""
    print(f"DEBUG: save_scroll_time_data called with page_id={page_id}")
    
    try:
        # پیدا کردن صفحه
        from wagtail.models import Page
        page = Page.objects.get(id=page_id)
        print(f"DEBUG: Found page: {page.title} - Type: {type(page.specific)}")
        
        # تبدیل به ScrollTimePage
        if not isinstance(page.specific, ScrollTimePage):
            raise Exception(f"صفحه از نوع ScrollTimePage نیست. نوع فعلی: {type(page.specific)}")
            
        scroll_page = page.specific
        print(f"DEBUG: ScrollTimePage API URL: {scroll_page.api_url}")
        
        if not scroll_page.api_url:
            raise Exception("آدرس API تنظیم نشده است")
            
        # فراخوانی متد ذخیره داده‌ها
        success, message = scroll_page.save_data_from_api()
        print(f"DEBUG: save_data_from_api returned: success={success}, message={message}")
        
        if success:
            messages.success(request, f"✅ {message}")
            print(f"SUCCESS: {message}")
        else:
            messages.error(request, f"❌ {message}")
            print(f"ERROR: {message}")
            
    except ScrollTimePage.DoesNotExist:
        error_msg = f"صفحه ScrollTimePage با ID {page_id} یافت نشد"
        messages.error(request, error_msg)
        print(f"ERROR: {error_msg}")
    except Exception as e:
        error_msg = f"خطا در ذخیره داده‌ها: {str(e)}"
        messages.error(request, error_msg)
        print(f"ERROR: {error_msg}")
        import traceback
        print(f"TRACEBACK: {traceback.format_exc()}")
    
    print(f"DEBUG: Redirecting to wagtailadmin_pages:edit with page_id={page_id}")
    return redirect('wagtailadmin_pages:edit', page_id)


@hooks.register('insert_editor_js')
def scroll_time_editor_js():
    """اضافه کردن جاوااسکریپت برای دکمه ذخیره داده‌ها"""
    return """
    <script>
    console.log('ScrollTime JavaScript loaded!');
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded, checking for ScrollTimePage...');
        
        // بررسی اینکه آیا در صفحه edit هستیم
        var currentUrl = window.location.pathname;
        console.log('Current URL:', currentUrl);
        
        // بررسی برای هر دو نوع URL
        if ((currentUrl.includes('/pages/') && currentUrl.includes('/edit/')) || 
            (currentUrl.includes('/scroll-time/') && currentUrl.includes('/preview/'))) {
            
            // استخراج page ID از URL
            var pageIdMatch = currentUrl.match(/\/pages\/(\d+)\/edit\//) || 
                             currentUrl.match(/\/scroll-time\/(\d+)\/preview\//);
            
            if (pageIdMatch) {
                var pageId = pageIdMatch[1];
                console.log('Found page ID:', pageId);
                
                // همیشه دکمه را اضافه کن اگر در صفحه scroll-time هستیم
                if (currentUrl.includes('scroll-time')) {
                    console.log('ScrollTime page detected, adding button...');
                    addSaveDataButton(pageId);
                } else {
                    // بررسی اینکه آیا فیلد api_url وجود دارد
                    var apiUrlField = document.querySelector('input[name="api_url"]');
                    if (apiUrlField) {
                        console.log('API URL field found, adding button...');
                        addSaveDataButton(pageId);
                    } else {
                        console.log('No API URL field found');
                    }
                }
            } else {
                console.log('No page ID found in URL');
            }
        } else {
            console.log('Not in edit/preview page');
        }
    });
    
    function addSaveDataButton(pageId) {
        console.log('Adding save data button for page:', pageId);
        
        // پیدا کردن container مناسب
        var actionsContainer = document.querySelector('.actions') || 
                              document.querySelector('.tab-content') ||
                              document.querySelector('.content-wrapper') ||
                              document.querySelector('form');
        
        console.log('Actions container:', actionsContainer);
        
        if (actionsContainer && !document.getElementById('save-data-btn')) {
            var saveButton = document.createElement('button');
            saveButton.id = 'save-data-btn';
            saveButton.type = 'button';
            saveButton.className = 'button button-primary';
            saveButton.textContent = 'ذخیره اطلاعات از API';
            saveButton.style.marginLeft = '10px';
            saveButton.style.backgroundColor = '#007cba';
            saveButton.style.color = 'white';
            saveButton.style.padding = '0.75em 1.5em';
            saveButton.style.borderRadius = '3px';
            saveButton.style.border = 'none';
            saveButton.style.cursor = 'pointer';
            saveButton.style.display = 'inline-block';
            
            saveButton.onclick = function(e) {
                e.preventDefault();
                console.log('Save button clicked!');
                
                if (confirm('آیا از ذخیره داده‌ها از API اطمینان دارید؟')) {
                    saveButton.textContent = 'در حال ذخیره...';
                    saveButton.style.backgroundColor = '#666';
                    saveButton.disabled = true;
                    
                    var saveUrl = '/sufobadmin/scroll-time/' + pageId + '/save-data/';
                    console.log('Redirecting to:', saveUrl);
                    window.location.href = saveUrl;
                }
            };
            
            // اضافه کردن دکمه در ابتدای container
            if (actionsContainer.firstChild) {
                actionsContainer.insertBefore(saveButton, actionsContainer.firstChild);
            } else {
                actionsContainer.appendChild(saveButton);
            }
            
            console.log('Save data button added successfully!');
        } else {
            console.log('Could not add button - container not found or button already exists');
        }
    }
    </script>
    """


@hooks.register('insert_editor_css')
def scroll_time_editor_css():
    """استایل برای دکمه ذخیره داده‌ها"""
    return """
    <style>
    #save-data-btn:hover {
        background-color: #005a87 !important;
        border-color: #005a87 !important;
    }
    </style>
    """