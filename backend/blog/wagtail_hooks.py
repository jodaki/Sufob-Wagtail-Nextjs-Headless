from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)

from .models import BlogCategory


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
