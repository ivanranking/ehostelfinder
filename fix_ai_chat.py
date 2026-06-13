import re
from pathlib import Path

# Read views.py
views_path = Path('hostels/views.py')
content = views_path.read_text()

# New ai_chat function with fallback to local AI
new_ai_chat = '''@csrf_exempt
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
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        # Network errors or API unavailable - use local AI fallback
        ai_response = get_local_ai_response(question)
        return JsonResponse({
            'candidates': [{
                'content': {
                    'parts': [{'text': ai_response}]
                }
            }]
        })
    except Exception:
        # For other errors, still use local AI fallback
        ai_response = get_local_ai_response(question)
        return JsonResponse({
            'candidates': [{
                'content': {
                    'parts': [{'text': ai_response}]
                }
            }]
        })'''

# Find and replace the ai_chat function using regex
# Match from @csrf_exempt decorator to the next @require_http_methods decorator
pattern = r'@csrf_exempt\s+@require_http_methods\(\[\'POST\'\]\)\s+def ai_chat\(request\):.*?(?=@require_http_methods\(\["GET"\]\)\s+def get_messages_by_hostel)'

replacement = new_ai_chat + '\n\n'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
views_path.write_text(content)
print('ai_chat function updated successfully')
