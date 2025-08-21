from django.contrib import admin
from .models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'original_name', 'user', 'status', 'progress', 
        'file_size', 'mime_type', 'created_at'
    ]
    list_filter = ['status', 'mime_type', 'created_at']
    search_fields = ['original_name', 'user__email', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'file_size', 'mime_type']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'original_name', 'file')
        }),
        ('File Info', {
            'fields': ('file_size', 'mime_type', 'status', 'progress')
        }),
        ('Content', {
            'fields': ('parsed_content', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )