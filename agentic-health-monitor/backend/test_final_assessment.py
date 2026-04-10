import json
from urllib.request import Request, urlopen

url = 'http://127.0.0.1:8000/final-assessment'
payload = {
    'original_data': {
        'name': 'Test',
        'age': 30,
        'gender': 'female',
        'symptoms': 'fever and headache',
        'duration': '2 days',
        'severity': 'moderate',
        'history': 'none',
        'bp': '120/80',
        'sugar': '110',
        'temperature': '100 F'
    },
    'follow_up_answers': {
        'question_0': '2 days',
        'question_1': 'no',
        'question_2': 'no'
    }
}
req = Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urlopen(req) as resp:
    print(resp.status)
    print(resp.read().decode('utf-8'))
