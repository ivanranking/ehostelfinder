from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Hostel, Booking, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_image_url')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'price', 'rating', 'available', 'created_at')
    list_filter = ('available', 'university', 'created_at')
    search_fields = ('name', 'university', 'description')
    list_editable = ('available',)
    ordering = ('-created_at',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'hostel', 'check_in', 'check_out', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at', 'check_in', 'check_out')
    search_fields = ('user__email', 'hostel__name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'hostel', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'hostel__name', 'subject', 'content')
    ordering = ('-created_at',)
