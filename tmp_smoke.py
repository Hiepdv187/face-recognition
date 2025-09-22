import requests, glob, time
images = []
images += glob.glob('samples/*.jpg')
images += glob.glob('dataset/*.jpg')
print('Will test images:', images)
for p in images:
    with open(p,'rb') as f:
        try:
            r = requests.post('http://127.0.0.1:5000/api/face/recognize', files={'image': f})
            print('\n---', p)
            print(r.status_code)
            print(r.text)
        except Exception as e:
            print('Error posting', p, e)
    time.sleep(0.4)
print('\nDone')
