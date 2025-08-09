#!/usr/bin/env python
"""
Setup script for Delivery Tracking Platform
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Django Settings
SECRET_KEY=django-insecure-your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Tracking Settings
TRACKING_LINK_EXPIRY_DAYS=30
TRACKING_LINK_SECRET_LENGTH=32

# Database Settings (for PostgreSQL)
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=delivery_tracker
# DB_USER=your_username
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✓ Created .env file with default settings")
    else:
        print("✓ .env file already exists")

def main():
    """Main setup function"""
    print("🚚 Delivery Tracking Platform Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    if not Path('venv').exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Run Django migrations
    if not run_command(f"{activate_cmd} && python manage.py makemigrations", "Creating Django migrations"):
        sys.exit(1)
    
    if not run_command(f"{activate_cmd} && python manage.py migrate", "Running Django migrations"):
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("2. Create a superuser (optional):")
    print("   python manage.py createsuperuser")
    
    print("3. Run the development server:")
    print("   python manage.py runserver")
    
    print("4. Access the application:")
    print("   - Dashboard: http://localhost:8000/")
    print("   - Admin: http://localhost:8000/admin/")
    print("   - API: http://localhost:8000/api/")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
