import requests

print('DEBUG:')
try:
    r = requests.get('http://127.0.0.1:5000/api/face/debug')
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('DEBUG ERROR:', e)

print('\nCOMPARE:')
try:
    r2 = requests.post('http://127.0.0.1:5000/api/face/compare?k=3', files={'image': open('samples/a.jpg','rb')}, timeout=30)
    print(r2.status_code)
    print(r2.text[:1000])
except Exception as e:
    print('COMPARE ERROR:', e)
