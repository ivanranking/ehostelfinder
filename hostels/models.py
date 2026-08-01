from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import uuid
import secrets


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


class User(AbstractUser):
    username = None
    id = models.CharField(max_length=255, primary_key=True, default=generate_user_id, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_image_url = models.URLField(blank=True, null=True)
    provider = models.CharField(max_length=50, default='email')
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('customer', 'Customer'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    hostel = models.ForeignKey('Hostel', on_delete=models.SET_NULL, blank=True, null=True, related_name='managers')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class Hostel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    university = models.CharField(max_length=255, blank=True, null=True)
    distance = models.CharField(max_length=255, blank=True, null=True, default='Near campus')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, default=0)
    amenities = models.JSONField(default=list, blank=True)
    contact = models.CharField(max_length=255, blank=True, null=True)
    available = models.BooleanField(default=True)
    is_full = models.BooleanField(default=False, help_text="Set to True when all rooms are occupied")
    total_floors = models.PositiveIntegerField(default=1, help_text="Total number of floors in the building")
    image_url = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    check_in_time = models.TimeField(default='14:00:00')
    check_out_time = models.TimeField(default='11:00:00')
    review_count = models.PositiveIntegerField(default=0)
    room_label_range = models.JSONField(default=dict, blank=True, help_text="Stores room label type, start, end, and floor count")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)

    def available_rooms_count(self):
        return self.rooms.filter(is_available=True, status='Available').count()

    def update_full_status(self):
        total_rooms = self.rooms.count()
        if total_rooms == 0:
            self.is_full = False
        else:
            available_rooms = self.rooms.filter(is_available=True, status='Available').count()
            self.is_full = available_rooms == 0
        self.save(update_fields=['is_full'])


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    is_cover = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.hostel.name} - Image {self.id}"


class HostelFacility(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='facilities')
    facility_name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.hostel.name} - {self.facility_name}"


class RoomType(models.TextChoices):
    SINGLE = 'Single', 'Single'
    DOUBLE = 'Double', 'Double'
    TRIPLE = 'Triple', 'Triple'
    QUADRUPLE = 'Quadruple', 'Quadruple'
    FAMILY = 'Family', 'Family'
    DORMITORY = 'Dormitory', 'Dormitory'
    SUITE = 'Suite', 'Suite'


class RoomStatus(models.TextChoices):
    AVAILABLE = 'Available', 'Available'
    OCCUPIED = 'Occupied', 'Occupied'
    MAINTENANCE = 'Maintenance', 'Maintenance'


class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=RoomType.choices)
    capacity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField(default=1)
    price_per_semester = models.DecimalField(max_digits=10, decimal_places=2)
    single_bed_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Price per single bed in shared rooms")
    floor = models.IntegerField(blank=True, null=True, help_text="Floor number in the building")
    description = models.TextField(blank=True, null=True)
    size_sq_meters = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    private_bathroom = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    television = models.BooleanField(default=False)
    wifi = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=RoomStatus.choices, default=RoomStatus.AVAILABLE)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number} ({self.room_name})"

    @property
    def is_shared_room(self):
        return self.room_type in ['Double', 'Triple', 'Quadruple', 'Dormitory']


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.room.room_name} - Image {self.id}"


class BookingStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    CONFIRMED = 'Confirmed', 'Confirmed'
    CHECKED_IN = 'Checked In', 'Checked In'
    CHECKED_OUT = 'Checked Out', 'Checked Out'
    CANCELLED = 'Cancelled', 'Cancelled'


class Booking(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    students = models.PositiveIntegerField()
    semesters = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    booking_reference = models.CharField(max_length=50, unique=True)
    payment_status = models.CharField(max_length=20, default='Pending')
    special_requests = models.TextField(blank=True, null=True)
    booked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['hostel', 'booking_status', 'check_in']),
            models.Index(fields=['room', 'check_in', 'check_out']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['payment_status']),
        ]

    def __str__(self):
        return f"{self.booking_reference} - {self.customer.email}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_booking_reference():
        import random
        import string
        ref = f"BK-{timezone.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        while Booking.objects.filter(booking_reference=ref).exists():
            ref = f"BK-{timezone.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        return ref


class PaymentMethod(models.TextChoices):
    CASH = 'Cash', 'Cash'
    CREDIT_CARD = 'Credit Card', 'Credit Card'
    BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'
    MOBILE_MONEY = 'Mobile Money', 'Mobile Money'
    ACCOUNT = 'Account', 'Account'
    USSD = 'USSD', 'USSD'
    ENAIRA = 'Enaira', 'Enaira'
    APPLE_PAY = 'Apple Pay', 'Apple Pay'
    GOOGLE_PAY = 'Google Pay', 'Google Pay'


class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    PAID = 'Paid', 'Paid'
    FAILED = 'Failed', 'Failed'
    REFUNDED = 'Refunded', 'Refunded'


class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    flw_ref = models.CharField(max_length=100, blank=True, null=True, help_text="Flutterwave reference")
    flutterwave_method = models.CharField(max_length=50, blank=True, null=True, help_text="Specific Flutterwave payment method")
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True, help_text="Stripe Payment Intent ID")
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.booking.booking_reference} - {self.amount} ({self.payment_status})"


class Review(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('hostel', 'customer')
        indexes = [
            models.Index(fields=['hostel', 'rating']),
        ]

    def __str__(self):
        return f"{self.hostel.name} - {self.customer.email} ({self.rating}/5)"


class Favorite(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('customer', 'hostel')
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['hostel']),
        ]

    def __str__(self):
        return f"{self.customer.email} - {self.hostel.name}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class Message(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='messages')
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    subject = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.hostel.name}"


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


class EmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_confirmations')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    confirmed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    def __str__(self):
        return f"EmailConfirmation for {self.user.email}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None

    def __str__(self):
        return f"PasswordResetToken for {self.user.email}"


# ========== ROOMMATE FINDER ==========

class RoommateRequest(models.Model):
    GENDER_CHOICES = (
        ('any', 'Any'),
        ('male', 'Male'),
        ('female', 'Female'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roommate_requests')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='roommate_requests')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, related_name='roommate_requests')
    preferred_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='any')
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    about_me = models.TextField(blank=True, default='')
    lifestyle_preferences = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['hostel', 'is_active']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} looking at {self.hostel.name}"


class ChatRoom(models.Model):
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, blank=True, null=True, related_name='chat_rooms')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['hostel']),
        ]

    def __str__(self):
        participants_list = list(self.participants.all()[:2])
        names = [p.get_full_name() or p.email for p in participants_list]
        return f"Chat: {', '.join(names)}"

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatMessage(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages', blank=True, null=True)
    content = models.TextField()
    is_ai = models.BooleanField(default=False, help_text="True if message sent by AI assistant")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat_room', 'created_at']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        sender = self.sender.email if self.sender else "AI"
        return f"{sender}: {self.content[:50]}"
