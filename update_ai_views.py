from pathlib import Path

# Read the current views file
views_path = Path('hostels/views.py')
content = views_path.read_text()

# Add the import for local_ai
import_section = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
import json
import os
import urllib.request
import urllib.error
from .forms import UserRegistrationForm, UserLoginForm
from .models import Hostel, Message as DjangoMessage, User, Booking as DjangoBooking, ContactMessage
from .local_ai import get_local_ai_response"""

old_import = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
import json
import os
import urllib.request
import urllib.error
from .forms import UserRegistrationForm, UserLoginForm
from .models import Hostel, Message as DjangoMessage, User, Booking as DjangoBooking, ContactMessage"""

content = content.replace(old_import, import_section)

# Replace the ai_chat function
old_ai_chat = """@csrf_exempt
@require_http_methods(['POST'])
def ai_chat(request):
    try:
        data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'Question is required.'}, status=400)

        api_key = os.getenv('GOOGLE_GENERATIVE_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'AI API key not configured.'}, status=500)

        prompt = (
            'You are a helpful hostel assistant for EHostelFinder. Answer questions about hostel services, bookings, and amenities. '
            'Be friendly, concise, and helpful. Context: EHostelFinder helps students find safe, comfortable, affordable accommodation near universities. '
            f'Question: {question}'
        )
        payload = json.dumps({
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }]
        }).encode('utf-8')
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = resp.read().decode('utf-8')
            result = json.loads(resp_data)

        return JsonResponse(result)
    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode('utf-8')
            error_json = json.loads(error_data)
            message = error_json.get('error', error_json.get('message', str(e)))
        except Exception:
            message = str(e)
        return JsonResponse({'error': message}, status=e.code if hasattr(e, 'code') else 500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)"""

new_ai_chat = """@csrf_exempt
@require_http_methods(['POST'])
def ai_chat(request):
    try:
        data = json.loads(request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body)
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'Question is required.'}, status=400)

        api_key = os.getenv('GOOGLE_GENERATIVE_API_KEY')
        if not api_key:
            # Use local AI fallback when API key is not configured
            ai_response = get_local_ai_response(question)
            return JsonResponse({
                'candidates': [{
                    'content': {
                        'parts': [{'text': ai_response}]
                    }
                }]
            })

        prompt = (
            'You are a helpful hostel assistant for EHostelFinder. Answer questions about hostel services, bookings, and amenities. '
            'Be friendly, concise, and helpful. Context: EHostelFinder helps students find safe, comfortable, affordable accommodation near universities. '
            f'Question: {question}'
        )
        payload = json.dumps({
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }]
        }).encode('utf-8')
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_data = resp.read().decode('utf-8')
            result = json.loads(resp_data)

        return JsonResponse(result)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
        # Network errors or API unavailable - use local AI fallback
        ai_response = get_local_ai_response(question)
        return JsonResponse({
            'candidates': [{
                'content': {
                    'parts': [{'text': ai_response}]
                }
            }]
        })
    except Exception as e:
        # For other errors, still use local AI fallback
        ai_response = get_local_ai_response(question)
        return JsonResponse({
            'candidates': [{
                'content': {
                    'parts': [{'text': ai_response}]
                }
            }]
        })"""

content = content.replace(old_ai_chat, new_ai_chat)

# Write back to file
views_path.write_text(content)
print("Updated views.py with local AI fallback system")
