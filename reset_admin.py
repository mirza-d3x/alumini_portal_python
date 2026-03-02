import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
try:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin')
    admin_user.role = 'ADMIN'
    admin_user.is_approved = True
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print("Admin password reset to 'admin'")
except User.DoesNotExist:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    admin_user.role = 'ADMIN'
    admin_user.is_approved = True
    admin_user.save()
    print("Admin user created with password 'admin'")
