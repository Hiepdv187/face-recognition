import requests
r = requests.post('http://127.0.0.1:5000/api/face/compare?k=5', files={'image': open('samples/a.jpg','rb')})
print('STATUS', r.status_code)
print(r.text)
