import requests

BASE_URL = "http://localhost:5000"

# Test đăng ký người mới
def test_register(name, image_path):
    url = f"{BASE_URL}/face-register"
    files = {"file": open(image_path, "rb")}
    data = {"name": name}
    response = requests.post(url, files=files, data=data)
    print("👉 Register:", response.json())


# Test nhận diện khuôn mặt
def test_recognition(image_path):
    url = f"{BASE_URL}/face-recognition"
    files = {"file": open(image_path, "rb")}
    response = requests.post(url, files=files)
    print("👉 Recognition:", response.json())


if __name__ == "__main__":
    # Ảnh để đăng ký người mới
    test_register("Hiep", "samples/a.jpg")

    # Ảnh để nhận diện
    test_recognition("samples/a.jpg")
