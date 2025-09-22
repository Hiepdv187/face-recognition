import requests

REG_URL = 'http://127.0.0.1:5000/api/face/register'
REC_URL = 'http://127.0.0.1:5000/api/face/recognize?fast=1'

# 1) Register
with open('samples/a.jpg','rb') as f:
    files = {'image': ('a.jpg', f, 'image/jpeg')}
    data = {'name': 'TestUser_A'}
    r = requests.post(REG_URL, files=files, data=data)
    print('REGISTER', r.status_code, r.text)

# 2) Recognize
with open('samples/a.jpg','rb') as f:
    files = {'image': ('a.jpg', f, 'image/jpeg')}
    r = requests.post(REC_URL, files=files)
    print('RECOGNIZE', r.status_code, r.text)
