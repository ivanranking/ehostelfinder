from django import forms
from django.contrib import admin
from .models import User, Profile, Hostel, HostelImage, HostelFacility, Room, RoomImage, Booking, Payment, Review, Favorite, Notification, Message, ContactMessage, EmailConfirmation


class HostelAdminForm(forms.ModelForm):
    single_price = forms.DecimalField(required=False, min_value=0, label='Single Price')
    double_price = forms.DecimalField(required=False, min_value=0, label='Double Price')
    triple_price = forms.DecimalField(required=False, min_value=0, label='Triple Price')
    quadruple_price = forms.DecimalField(required=False, min_value=0, label='Quadruple Price')
    amenities = forms.CharField(required=False, widget=forms.TextInput, label='Amenities')

    class Meta:
        model = Hostel
        fields = ['name', 'description', 'address', 'city', 'university', 'rating', 'amenities', 'image_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['single_price'].initial = self.instance.price
            self.fields['double_price'].initial = self.instance.price
            self.fields['triple_price'].initial = self.instance.price
            self.fields['quadruple_price'].initial = self.instance.price
            if isinstance(self.instance.amenities, list):
                self.fields['amenities'].initial = ', '.join(self.instance.amenities)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.country = 'Unknown'
        instance.price = self.cleaned_data.get('single_price') or 0
        amenities_text = self.cleaned_data.get('amenities') or ''
        instance.amenities = [item.strip() for item in amenities_text.split(',') if item.strip()]
        if commit:
            instance.save()
        return instance


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_email_verified', 'provider', 'created_at']
    list_filter = ['is_email_verified', 'provider', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'role', 'hostel', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    raw_id_fields = ['user', 'hostel']


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    form = HostelAdminForm
    fields = ['name', 'description', 'address', 'city', 'university', 'single_price', 'double_price', 'triple_price', 'quadruple_price', 'rating', 'amenities', 'image_url']
    list_display = ['name', 'city', 'country', 'university', 'price', 'rating', 'available']
    list_filter = ['city', 'country', 'university', 'available']
    search_fields = ['name', 'address', 'city', 'university']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'room_number', 'room_name', 'room_type', 'price_per_night', 'status']
    list_filter = ['room_type', 'status', 'hostel']
    search_fields = ['room_number', 'room_name', 'hostel__name']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'customer', 'hostel', 'room', 'check_in', 'check_out', 'booking_status', 'payment_status']
    list_filter = ['booking_status', 'payment_status', 'check_in']
    search_fields = ['booking_reference', 'customer__email', 'hostel__name']
    raw_id_fields = ['customer', 'hostel', 'room']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_method', 'payment_status', 'paid_at']
    list_filter = ['payment_method', 'payment_status']
    search_fields = ['booking__booking_reference', 'transaction_reference']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['hostel__name', 'customer__email']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'hostel', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer__email', 'hostel__name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__email', 'title']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'full_name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'email', 'subject', 'hostel__name']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'email', 'subject']


@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'expires_at', 'confirmed_status', 'created_at']
    list_filter = ['confirmed_at', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at', 'expires_at']

    @admin.display(boolean=True, description='Confirmed')
    def confirmed_status(self, obj):
        return obj.is_confirmed
