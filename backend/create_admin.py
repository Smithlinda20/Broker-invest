#!/usr/bin/env python
"""
Initialize admin user for custom admin panel
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'broker_core.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from admin_panel.models import AdminUser

def create_admin_user():
    """Create default admin user if not exists"""
    admin_email = 'Vera@admin.com'
    admin_password = 'AdminVera'
    admin_name = 'Vera'
    
    admin_exists = AdminUser.objects.filter(email=admin_email).exists()
    
    if admin_exists:
        print("✓ Admin user already exists")
        admin = AdminUser.objects.get(email=admin_email)
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.name}")
    else:
        admin = AdminUser.objects.create(
            email=admin_email,
            password=make_password(admin_password),
            name=admin_name,
            is_active=True
        )
        print("✅ Admin user created successfully!")
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.name}")
        print(f"  Login: /backend/login/")

if __name__ == '__main__':
    create_admin_user()
