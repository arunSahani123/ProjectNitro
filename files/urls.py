from django.urls import path
from . import views

urlpatterns = [
    # File operations
    path('files/', views.FileUploadView.as_view(), name='file-upload'),
    path('files/list/', views.FileListView.as_view(), name='file-list'),
    path('files/<uuid:pk>/', views.FileDetailView.as_view(), name='file-detail'),
    path('files/<uuid:file_id>/progress/', views.file_progress_view, name='file-progress'),
    
    # Health and docs
    path('health/', views.health_check_view, name='health-check'),
    path('docs/', views.api_docs_view, name='api-docs'),
]