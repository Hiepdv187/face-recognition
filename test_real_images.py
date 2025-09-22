import requests
import os

# Test API nhận diện với hình ảnh thật từ dataset
def test_recognition_with_real_images():
    dataset_dir = r"f:\face-recognition\dataset"

    # Lấy danh sách files trong dataset
    image_files = [f for f in os.listdir(dataset_dir) if f.endswith('.jpg')]

    if not image_files:
        print("❌ No images found in dataset")
        return

    print(f"📁 Found {len(image_files)} images in dataset")

    for i, image_file in enumerate(image_files[:3]):  # Test 3 images đầu tiên
        image_path = os.path.join(dataset_dir, image_file)

        try:
            print(f"\n🧪 Testing image {i+1}: {image_file}")

            with open(image_path, 'rb') as f:
                files = {'image': (image_file, f, 'image/jpeg')}
                response = requests.post('http://localhost:5000/api/face/recognize', files=files)

            print(f"📡 Response Status: {response.status_code}")
            print(f"📄 Response JSON: {response.json()}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_recognition_with_real_images()
