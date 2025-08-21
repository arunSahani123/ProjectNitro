#!/usr/bin/env python
"""
Setup script for File Parser API
This script helps set up the development environment
"""

import os
import sys
import subprocess
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a shell command and print status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Check if required services are running"""
    print("\n🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is installed")
    
    # Check Redis
    redis_check = subprocess.run("redis-cli ping", shell=True, capture_output=True, text=True)
    if redis_check.returncode == 0:
        print("✅ Redis is running")
    else:
        print("⚠️  Redis is not running. Please start Redis server:")
        print("   - Windows: redis-server")
        print("   - macOS: brew services start redis") 
        print("   - Ubuntu: sudo systemctl start redis")
        return False
    
    return True

def setup_django():
    """Setup Django project"""
    print("\n🚀 Setting up Django project...")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_parser_project.settings')
    django.setup()
    
    # Run migrations
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create directories
    os.makedirs('media/uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print("✅ Created required directories")
    
    # Collect static files
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    print("✅ Static files collected")
    
    return True

def create_superuser():
    """Create superuser if requested"""
    create = input("\n❓ Do you want to create a superuser? (y/N): ").lower().strip()
    if create == 'y':
        execute_from_command_line(['manage.py', 'createsuperuser'])

def main():
    """Main setup function"""
    print("🎯 File Parser API Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed. Please resolve the issues above.")
        sys.exit(1)
    
    # Setup Django
    if not setup_django():
        print("\n❌ Django setup failed.")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Start Celery worker: celery -A file_parser_project worker --loglevel=info")
    print("3. Visit http://localhost:8000/swagger/ for API documentation")
    print("4. Visit http://localhost:8000/admin/ for admin interface")

if __name__ == '__main__':
    main()