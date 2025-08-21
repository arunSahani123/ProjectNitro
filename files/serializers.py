from rest_framework import serializers
from .models import FileUpload


class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    file_url = serializers.ReadOnlyField()
    
    class Meta:
        model = FileUpload
        fields = [
            'id', 'filename', 'original_name', 'file', 'file_size', 
            'mime_type', 'status', 'progress', 'created_at', 'updated_at', 'file_url'
        ]
        read_only_fields = [
            'id', 'filename', 'file_size', 'mime_type', 'status', 
            'progress', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        file_obj = validated_data['file']
        validated_data['original_name'] = file_obj.name
        validated_data['filename'] = file_obj.name
        validated_data['file_size'] = file_obj.size
        validated_data['mime_type'] = file_obj.content_type or 'application/octet-stream'
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = [
            'id', 'filename', 'original_name', 'file_size', 'mime_type',
            'status', 'progress', 'created_at', 'updated_at'
        ]


class FileProgressSerializer(serializers.ModelSerializer):
    file_id = serializers.CharField(source='id')
    
    class Meta:
        model = FileUpload
        fields = ['file_id', 'status', 'progress']


class FileContentSerializer(serializers.ModelSerializer):
    content = serializers.JSONField(source='parsed_content')
    
    class Meta:
        model = FileUpload
        fields = ['id', 'filename', 'original_name', 'status', 'content']