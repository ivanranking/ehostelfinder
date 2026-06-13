import http.client
import json

conn = http.client.HTTPConnection('127.0.0.1', 8000, timeout=10)
body = json.dumps({'question': 'What amenities are available?'})
headers = {'Content-Type': 'application/json'}
try:
    conn.request('POST', '/api/ai-chat/', body, headers)
    resp = conn.getresponse()
    print(resp.status)
    print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
finally:
    conn.close()
