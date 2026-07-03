from django import forms
from .models import Booking, Hostel, Message, User, Profile


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room', 'check_in', 'check_out', 'guests', 'special_requests']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['hostel', 'full_name', 'email', 'phone', 'subject', 'content']


class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = '__all__'


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    terms = forms.BooleanField(required=True, label="I agree to the Terms of Service and Privacy Policy")
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'terms']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_email_verified = True
        import uuid
        user.id = str(uuid.uuid4())
        if commit:
            user.save()
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'email': user.email,
                    'role': 'customer'
                }
            )
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email Address")


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
        if new_password and len(new_password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'phone', 'profile_photo']
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.email = profile.user.email
        if commit:
            profile.save()
        return profile


class ManagerProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'email', 'phone', 'profile_photo']
    
    def save(self, commit=True, user=None, hostel=None):
        profile = super().save(commit=False)
        profile.user = user
        profile.role = 'manager'
        profile.hostel = hostel
        if commit:
            profile.save()
        return profile


class HostelUploadForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100, required=False)
    university = forms.CharField(max_length=255, required=False)
    price_single = forms.DecimalField(required=False, min_value=0)
    price_double = forms.DecimalField(required=False, min_value=0)
    price_triple = forms.DecimalField(required=False, min_value=0)
    price_quadruple = forms.DecimalField(required=False, min_value=0)
    rating = forms.DecimalField(required=False, min_value=0, max_value=5)
    amenities = forms.CharField(required=False)
    image_url = forms.URLField(required=False)