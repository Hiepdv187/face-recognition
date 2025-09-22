import requests
import numpy as np
from PIL import Image
import io

# Tạo hình ảnh test đơn giản
def create_test_image():
    # Tạo ảnh 100x100 pixel với màu ngẫu nhiên
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    return img

# Test API nhận diện với hình ảnh test
def test_recognition():
    # Tạo hình ảnh test
    test_img = create_test_image()

    # Chuyển đổi thành bytes
    img_bytes = io.BytesIO()
    test_img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # Gửi request
    try:
        files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
        response = requests.post('http://localhost:5000/api/face/recognize', files=files)

        print("📡 Response Status:", response.status_code)
        print("📄 Response JSON:", response.json())

    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    test_recognition()
