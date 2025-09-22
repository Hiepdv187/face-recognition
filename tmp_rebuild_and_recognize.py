import requests
print('Calling rebuild...')
r = requests.post('http://127.0.0.1:5000/api/face/rebuild')
print(r.status_code, r.text)
# Then run recognize
with open('samples/a.jpg','rb') as f:
    r2 = requests.post('http://127.0.0.1:5000/api/face/recognize?fast=1', files={'image': ('a.jpg', f, 'image/jpeg')})
    print('RECOGNIZE', r2.status_code, r2.text)
