from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from .models import User, EmailConfirmation, Profile
from .email_utils import send_email_confirmation
from .forms import UserRegistrationForm


@require_http_methods(['GET', 'POST'])
def signup_with_email_verification(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                send_email_confirmation(user, request)
            except Exception:
                pass
            messages.success(request, 'Please check your email to confirm your account before logging in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup_verification.html', {'form': form})


@require_http_methods(['GET'])
def confirm_email(request, token):
    try:
        confirmation = EmailConfirmation.objects.select_related('user').get(token=token)
        
        if confirmation.is_expired:
            return render(request, 'email_confirmation_status.html', {
                'status': 'expired',
                'message': 'This confirmation link has expired.'
            })
        
        if confirmation.is_confirmed:
            return render(request, 'email_confirmation_status.html', {
                'status': 'already_confirmed',
                'message': 'Your email was already confirmed.'
            })
        
        confirmation.confirmed_at = timezone.now()
        confirmation.save()
        
        user = confirmation.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        
        Profile.objects.get_or_create(
            user=user,
            defaults={
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
                'role': 'customer'
            }
        )
        
        return render(request, 'email_confirmation_status.html', {
            'status': 'success',
            'message': 'Your email has been confirmed! You can now log in.'
        })
    except EmailConfirmation.DoesNotExist:
        return render(request, 'email_confirmation_status.html', {
            'status': 'invalid',
            'message': 'Invalid confirmation link.'
        })


@require_http_methods(['POST'])
def resend_confirmation(request):
    email = request.POST.get('email') or request.GET.get('email')
    if not email:
        return JsonResponse({'error': 'Email is required'}, status=400)
    
    try:
        user = User.objects.get(email=email)
        EmailConfirmation.objects.filter(user=user).delete()
        send_email_confirmation(user, request)
        return JsonResponse({'success': True, 'message': 'Confirmation email sent.'})
    except User.DoesNotExist:
        return JsonResponse({'success': True, 'message': 'If the email exists, a confirmation will be sent.'})