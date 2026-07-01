import secrets
from datetime import timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone


def send_email_confirmation(user, request=None):
    from .models import EmailConfirmation
    
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=24)
    
    EmailConfirmation.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    if request:
        site_url = request.build_absolute_uri('/')
    else:
        site_url = 'http://localhost:8000'
    
    confirmation_url = f"{site_url.rstrip('/')}/confirm-email/{token}/"
    
    subject = "Confirm your email for EHostelFinder"
    message = render_to_string('emails/confirm_email.html', {
        'user': user,
        'confirmation_url': confirmation_url,
        'site_url': site_url,
    })
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email='noreply@ehostelfinder.com',
        to=[user.email],
    )
    email.content_subtype = 'html'
    email.send(fail_silently=True)
    
    return token


def send_welcome_email(user):
    subject = "Welcome to EHostelFinder!"
    message = render_to_string('emails/welcome.html', {
        'user': user,
    })
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email='noreply@ehostelfinder.com',
        to=[user.email],
    )
    email.content_subtype = 'html'
    email.send(fail_silently=True)


def send_password_reset_email(user, request):
    from .models import PasswordResetToken
    
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=1)
    
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )
    
    if request:
        site_url = request.build_absolute_uri('/')
    else:
        site_url = 'http://localhost:8000'
    
    reset_url = f"{site_url.rstrip('/')}/reset-password/{token}/"
    
    subject = "Reset your EHostelFinder password"
    message = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
        'site_url': site_url,
    })
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email='noreply@ehostelfinder.com',
        to=[user.email],
    )
    email.content_subtype = 'html'
    email.send(fail_silently=True)
    
    return token