from pathlib import Path

# update base.html
base_path = Path('templates/base.html')
text = base_path.read_text()
old = '''                const response = await fetch(
                    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyDST-CssEljn9b57fxyLzxPSsDvW3udlmA",
                    {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            contents: [{
                                parts: [{
                                    text: `You are a helpful hostel assistant for EHostelFinder. Answer questions about hostel services, bookings, and amenities. Be friendly, concise, and helpful. Context: EHostelFinder helps students find safe, comfortable, affordable accommodation near universities. Question: ${question}`
                                }]
                            }]
                        })
                    }
                );'''
new = '''                const response = await fetch("/api/ai-chat/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question })
                });'''
if old not in text:
    raise SystemExit('base.html snippet not found')
text = text.replace(old, new)
text = text.replace(
    '                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);\n\n                const data = await response.json();\n                let aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || \'Sorry, I could not generate a response.\';\n',
    '                let data = await response.json();\n                if (!response.ok) {\n                    const errMessage = data.error || data.message || `Server returned ${response.status}`;\n                    throw new Error(errMessage);\n                }\n                let aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || data.reply || \'Sorry, I could not generate a response.\';\n'
)
base_path.write_text(text)

# update hostels/views.py
views_path = Path('hostels/views.py')
text = views_path.read_text()
if 'import os' not in text:
    text = text.replace('import json\nfrom .forms import UserRegistrationForm, UserLoginForm\n', 'import json\nos\nimport urllib.request\nimport urllib.error\nfrom .forms import UserRegistrationForm, UserLoginForm\n')
if 'from django.views.decorators.csrf import csrf_exempt' not in text:
    text = text.replace('from django.views.decorators.http import require_http_methods\n', 'from django.views.decorators.http import require_http_methods\nfrom django.views.decorators.csrf import csrf_exempt\n')
if 'def ai_chat(request):' in text:
    raise SystemExit('ai_chat already exists')
insert_after = '    return JsonResponse(message, status=201)\n    except Exception as e:\n        return JsonResponse({\'error\': \'Failed to send message\'}, status=500)\n\n'
new_view = '''@csrf_exempt
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
        return JsonResponse({'error': str(e)}, status=500)
'''
if insert_after not in text:
    raise SystemExit('could not find insertion point in views.py')
text = text.replace(insert_after, insert_after + new_view)
views_path.write_text(text)

# update hostels/urls.py
urls_path = Path('hostels/urls.py')
text = urls_path.read_text()
if "path('api/ai-chat/'" not in text:
    text = text.replace("    path('api/messages/', views.create_message, name='api_create_message'),\n",
                        "    path('api/messages/', views.create_message, name='api_create_message'),\n    path('api/ai-chat/', views.ai_chat, name='api_ai_chat'),\n")
urls_path.write_text(text)

# update .env
env_path = Path('.env')
text = env_path.read_text()
if 'GOOGLE_GENERATIVE_API_KEY=' not in text:
    text += '\nGOOGLE_GENERATIVE_API_KEY=AIzaSyDST-CssEljn9b57fxyLzxPSsDvW3udlmA\n'
env_path.write_text(text)

print('patched ai route and frontend')