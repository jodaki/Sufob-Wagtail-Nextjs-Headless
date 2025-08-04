from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

class ImportExportMenuAdmin(admin.ModelAdmin):
    change_list_template = 'admin/import_export_menu.html'

    def changelist_view(self, request, extra_context=None):
        # فقط برای نمایش لینک در منو
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(type('ImportExportMenu', (object,), {}), ImportExportMenuAdmin)
