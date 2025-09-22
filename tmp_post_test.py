import requests
r = requests.post('http://127.0.0.1:5000/api/face/recognize?fast=1', files={'image': open('samples/a.jpg','rb')})
print(r.status_code)
print(r.headers.get('Content-Type'))
print(r.text)
