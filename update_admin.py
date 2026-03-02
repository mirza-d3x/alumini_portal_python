import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from portal.models import Profile
User = get_user_model()
admin_user = User.objects.get(username='admin')
if not hasattr(admin_user, 'profile'):
    Profile.objects.create(user=admin_user)
    print("Created profile for admin")
else:
    print("Profile already exists")
