from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Category


class CategoryAdmin(ModelAdmin):
    model = Category
    menu_label = 'دسته‌بندی‌ها'
    menu_icon = 'folder-open-inverse'
    list_display = ['name', 'value', 'is_active']
    search_fields = ['name']


# ثبت فقط Category در Wagtail Admin
modeladmin_register(CategoryAdmin)
