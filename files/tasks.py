import os
import json
import csv
import pandas as pd
import threading
import time
from io import StringIO
from PyPDF2 import PdfReader
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import FileUpload


def process_file_background(file_id):
    """Process file in background thread"""
    def process():
        try:
            file_upload = FileUpload.objects.get(id=file_id)
            
            # Update status to processing
            file_upload.status = 'processing'
            file_upload.progress = 10
            file_upload.processing_started_at = timezone.now()
            file_upload.save()
            
            # Cache progress for real-time updates
            cache.set(f'file_progress_{file_id}', {
                'status': 'processing',
                'progress': 10
            }, timeout=3600)
            
            # Get file path
            file_path = file_upload.file.path
            
            # Determine file type and parse accordingly
            if file_upload.mime_type.startswith('text/') or file_upload.original_name.endswith('.csv'):
                parsed_content = parse_csv_file(file_path, file_id)
            elif file_upload.mime_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                                           'application/vnd.ms-excel'] or file_upload.original_name.endswith(('.xlsx', '.xls')):
                parsed_content = parse_excel_file(file_path, file_id)
            elif file_upload.mime_type == 'application/pdf' or file_upload.original_name.endswith('.pdf'):
                parsed_content = parse_pdf_file(file_path, file_id)
            else:
                # For other file types, just store basic info
                parsed_content = {
                    'filename': file_upload.original_name,
                    'size': file_upload.file_size,
                    'type': file_upload.mime_type,
                    'message': 'File uploaded successfully. Parsing not supported for this file type.'
                }
            
            # Update progress
            file_upload.progress = 90
            file_upload.save()
            cache.set(f'file_progress_{file_id}', {
                'status': 'processing',
                'progress': 90
            }, timeout=3600)
            
            # Save parsed content
            file_upload.parsed_content = parsed_content
            file_upload.status = 'ready'
            file_upload.progress = 100
            file_upload.save()
            
            # Cache final progress
            cache.set(f'file_progress_{file_id}', {
                'status': 'ready',
                'progress': 100
            }, timeout=3600)
            
            print(f"File {file_id} processed successfully")
            
        except FileUpload.DoesNotExist:
            print(f"File {file_id} not found")
        except Exception as e:
            # Handle errors
            try:
                file_upload = FileUpload.objects.get(id=file_id)
                file_upload.status = 'failed'
                file_upload.error_message = str(e)
                file_upload.save()
                cache.set(f'file_progress_{file_id}', {
                    'status': 'failed',
                    'progress': file_upload.progress,
                    'error': str(e)
                }, timeout=3600)
            except:
                pass
            print(f"Error processing file {file_id}: {str(e)}")
    
    # Start processing in background thread
    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()


def parse_csv_file(file_path, file_id):
    """Parse CSV file and return structured data"""
    try:
        # Update progress
        update_progress(file_id, 'processing', 30)
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Update progress
            update_progress(file_id, 'processing', 50)
            
            for i, row in enumerate(reader):
                data.append(dict(row))
                # Update progress every 100 rows
                if i % 100 == 0:
                    progress = min(50 + (i * 30 / 1000), 80)
                    update_progress(file_id, 'processing', int(progress))
        
        return {
            'type': 'csv',
            'headers': list(data[0].keys()) if data else [],
            'rows': len(data),
            'data': data[:100],  # Limit to first 100 rows for API response
            'total_rows': len(data),
            'sample_data': data[:5] if data else []
        }
    except Exception as e:
        raise Exception(f"Error parsing CSV file: {str(e)}")


def parse_excel_file(file_path, file_id):
    """Parse Excel file and return structured data"""
    try:
        # Update progress
        update_progress(file_id, 'processing', 30)
        
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Update progress
        update_progress(file_id, 'processing', 60)
        
        # Convert to list of dictionaries
        data = df.to_dict('records')
        
        # Update progress
        update_progress(file_id, 'processing', 80)
        
        return {
            'type': 'excel',
            'headers': list(df.columns),
            'rows': len(data),
            'data': data[:100],  # Limit to first 100 rows
            'total_rows': len(data),
            'sample_data': data[:5] if data else [],
            'sheets': 1  # For simplicity, we're only reading the first sheet
        }
    except Exception as e:
        raise Exception(f"Error parsing Excel file: {str(e)}")


def parse_pdf_file(file_path, file_id):
    """Parse PDF file and extract text content"""
    try:
        # Update progress
        update_progress(file_id, 'processing', 30)
        
        reader = PdfReader(file_path)
        text_content = []
        
        total_pages = len(reader.pages)
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            text_content.append({
                'page': i + 1,
                'content': text
            })
            
            # Update progress
            progress = 30 + (i * 50 / total_pages)
            update_progress(file_id, 'processing', int(progress))
        
        # Combine all text
        full_text = ' '.join([page['content'] for page in text_content])
        
        return {
            'type': 'pdf',
            'pages': total_pages,
            'content': text_content,
            'full_text': full_text,
            'word_count': len(full_text.split()),
            'character_count': len(full_text)
        }
    except Exception as e:
        raise Exception(f"Error parsing PDF file: {str(e)}")


def update_progress(file_id, status, progress, error_message=None):
    """Update progress in cache and database"""
    try:
        # Update cache for real-time access
        progress_data = {
            'status': status,
            'progress': progress
        }
        if error_message:
            progress_data['error'] = error_message
            
        cache.set(f'file_progress_{file_id}', progress_data, timeout=3600)
        
        # Also update database
        file_upload = FileUpload.objects.get(id=file_id)
        file_upload.status = status
        file_upload.progress = progress
        if error_message:
            file_upload.error_message = error_message
        file_upload.save()
        
    except Exception as e:
        print(f"Error updating progress: {e}")