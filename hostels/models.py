from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import uuid

def generate_user_id():
    return str(uuid.uuid4())

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)
    
    def get_by_natural_key(self, email):
        return self.get(email=email)


import uuid

def generate_user_id():
    return str(uuid.uuid4())

class User(AbstractUser):
    username = None  # Remove username field, use email instead
    id = models.CharField(max_length=255, primary_key=True, default=generate_user_id, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_image_url = models.URLField(blank=True, null=True)
    provider = models.CharField(max_length=50, default='email')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email

class Hostel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    university = models.CharField(max_length=255)
    distance = models.CharField(max_length=100)
    price = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    review_count = models.IntegerField()
    image_url = models.URLField()
    amenities = models.JSONField(default=list)
    contact = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    total_price = models.IntegerField()
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.hostel.name}"

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.subject}"