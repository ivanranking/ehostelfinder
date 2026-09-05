import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehostelfinder.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

new_password = 'Ranking@ivan12'
users = User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True)

for user in users:
    user.set_password(new_password)
    user.save(update_fields=['password'])
    print(f"Password changed for: {user.email}")

print(f"\nAll {users.count()} admin/superuser account(s) updated with password: {new_password}")
