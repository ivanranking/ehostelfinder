from django import forms
from .models import Hostel, Booking, Message, User

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['hostel', 'full_name', 'email', 'phone', 'university', 'student_id', 'move_in_date', 'room_type', 'special_requests', 'status']
        widgets = {
            'status': forms.TextInput(attrs={'placeholder': 'pending'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['hostel', 'full_name', 'email', 'phone', 'message']

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = '__all__'

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
    
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
        import uuid
        user.id = str(uuid.uuid4())
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)