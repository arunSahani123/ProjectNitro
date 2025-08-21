import pytest
import tempfile
import os
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from files.models import FileUpload

User = get_user_model()


@pytest.mark.django_db
class TestFileOperations:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_file_upload(self):
        """Test file upload endpoint"""
        # Create a test CSV file
        csv_content = "Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles"
        uploaded_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        url = reverse('file-upload')
        response = self.client.post(url, {'file': uploaded_file}, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'file_id' in response.data
        assert response.data['status'] == 'uploading'

    def test_file_list(self):
        """Test file listing endpoint"""
        # Create a file record
        file_upload = FileUpload.objects.create(
            user=self.user,
            filename='test.csv',
            original_name='test.csv',
            file_size=100,
            mime_type='text/csv',
            status='ready'
        )
        
        url = reverse('file-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert str(response.data['results'][0]['id']) == str(file_upload.id)

    def test_file_progress(self):
        """Test file progress endpoint"""
        file_upload = FileUpload.objects.create(
            user=self.user,
            filename='test.csv',
            original_name='test.csv',
            file_size=100,
            mime_type='text/csv',
            status='processing',
            progress=50
        )
        
        url = reverse('file-progress', kwargs={'file_id': file_upload.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['progress'] == 50
        assert response.data['status'] == 'processing'

    def test_file_content_ready(self):
        """Test getting file content when ready"""
        file_upload = FileUpload.objects.create(
            user=self.user,
            filename='test.csv',
            original_name='test.csv',
            file_size=100,
            mime_type='text/csv',
            status='ready',
            progress=100,
            parsed_content={'data': 'test'}
        )
        
        url = reverse('file-detail', kwargs={'pk': file_upload.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'content' in response.data

    def test_file_content_processing(self):
        """Test getting file content while processing"""
        file_upload = FileUpload.objects.create(
            user=self.user,
            filename='test.csv',
            original_name='test.csv',
            file_size=100,
            mime_type='text/csv',
            status='processing',
            progress=50
        )
        
        url = reverse('file-detail', kwargs={'pk': file_upload.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert 'message' in response.data

    def test_file_delete(self):
        """Test file deletion"""
        file_upload = FileUpload.objects.create(
            user=self.user,
            filename='test.csv',
            original_name='test.csv',
            file_size=100,
            mime_type='text/csv',
            status='ready'
        )
        
        url = reverse('file-detail', kwargs={'pk': file_upload.id})
        response = self.client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not FileUpload.objects.filter(id=file_upload.id).exists()

    def test_unauthorized_access(self):
        """Test unauthorized access to file operations"""
        self.client.force_authenticate(user=None)
        
        url = reverse('file-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED