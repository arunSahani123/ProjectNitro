import os
import magic
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from .models import FileUpload
from .serializers import (
    FileUploadSerializer, FileListSerializer, 
    FileProgressSerializer, FileContentSerializer
)
from .tasks import process_file_background


class FileUploadView(generics.CreateAPIView):
    """File upload endpoint with progress tracking"""
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate file size
        file_obj = request.FILES.get('file')
        if file_obj.size > settings.MAX_FILE_SIZE:
            return Response({
                'error': f'File size too large. Maximum size is {settings.MAX_FILE_SIZE} bytes.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create file record
        file_upload = serializer.save()
        
        # Start background processing
        process_file_background(str(file_upload.id))
        
        return Response({
            'file_id': str(file_upload.id),
            'message': 'File uploaded successfully. Processing started.',
            'status': file_upload.status,
            'progress': file_upload.progress
        }, status=status.HTTP_201_CREATED)


class FileListView(generics.ListAPIView):
    """List all files for the authenticated user"""
    serializer_class = FileListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user)


class FileDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific file"""
    serializer_class = FileContentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        file_upload = self.get_object()
        
        if file_upload.status == 'processing' or file_upload.status == 'uploading':
            return Response({
                'message': 'File upload or processing in progress. Please try again later.',
                'status': file_upload.status,
                'progress': file_upload.progress
            }, status=status.HTTP_202_ACCEPTED)
        
        if file_upload.status == 'failed':
            return Response({
                'error': 'File processing failed.',
                'error_message': file_upload.error_message,
                'status': file_upload.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(file_upload)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def file_progress_view(request, file_id):
    """Get file upload/processing progress"""
    try:
        # First check cache for real-time progress
        cached_progress = cache.get(f'file_progress_{file_id}')
        if cached_progress:
            return Response({
                'file_id': file_id,
                **cached_progress
            })
        
        # Fallback to database
        file_upload = get_object_or_404(
            FileUpload, 
            id=file_id, 
            user=request.user
        )
        serializer = FileProgressSerializer(file_upload)
        return Response(serializer.data)
    except FileUpload.DoesNotExist:
        return Response({
            'error': 'File not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_view(request):
    """Health check endpoint"""
    return Response({
        'status': 'OK',
        'message': 'File Parser API is running',
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_docs_view(request):
    """API documentation endpoint"""
    return Response({
        'title': 'File Parser CRUD API',
        'version': '1.0.0',
        'description': 'API for uploading, parsing, and managing files with progress tracking',
        'authentication': 'JWT Bearer Token',
        'endpoints': {
            'POST /api/auth/register/': 'Register a new user',
            'POST /api/auth/login/': 'Login user',
            'POST /api/auth/logout/': 'Logout user',
            'GET /api/auth/profile/': 'Get user profile',
            'POST /api/files/': 'Upload a file',
            'GET /api/files/': 'List all files',
            'GET /api/files/{id}/': 'Get file content',
            'GET /api/files/{id}/progress/': 'Get file progress',
            'DELETE /api/files/{id}/': 'Delete a file',
            'GET /health/': 'Health check',
        },
        'websocket': 'ws://localhost:8000/ws/files/{file_id}/ for real-time progress updates'
    })