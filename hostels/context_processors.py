from django.conf import settings

def stripe_config(request):
    return {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
