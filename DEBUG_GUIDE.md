# 🔧 Face Recognition Debug Guide

Nếu hệ thống face recognition không nhận diện được faces đã đăng ký, hãy làm theo các bước sau:

## 📊 **Bước 1: Kiểm tra System Status**

1. **Mở trình duyệt** → `http://localhost:5000/realtime`
2. **Click "🔧 Debug"** để kiểm tra trạng thái hệ thống
3. **Kiểm tra Console** (F12 → Console) để xem logs

**Expected Result:**
```
✅ System Status: exists, exists
👥 Registered persons: 2
📁 Dataset files: 5
📝 Registered faces:
  - ID 1: Đặng Vũ Hiệp
  - ID 2: Bá Việt
```

## 🚨 **Bước 2: Khắc phục các vấn đề thường gặp**

### **Vấn đề 1: FAISS Index bị thiếu**
```
❌ System Status: missing, missing
```
**Giải pháp:**
```bash
# Reset database và embeddings
cd f:\face-recognition
python reset_db.py
```

### **Vấn đề 2: Không có faces đã đăng ký**
```
👥 Registered persons: 0
```
**Giải pháp:**
1. Click "👤 Register Face" để đăng ký face mới
2. Hoặc sử dụng API để đăng ký:
```bash
curl -X POST http://localhost:5000/api/face/register \
  -F "name=Test Person" \
  -F "image=@path/to/image.jpg"
```

### **Vấn đề 3: Recognition API không hoạt động**
**Kiểm tra:**
1. Mở Console (F12)
2. Click "🎥 Start Camera"
3. Xem logs trong Console

**Expected Logs:**
```
📹 Starting camera...
✅ Camera access granted
🎥 Video element configured
✅ Auto recognition started
🔄 Recognition cycle triggered
🎥 Capturing frame for recognition...
📊 Blob size: 12345 bytes
📡 Response status: 200
📄 Response JSON: {status: "success", name: "John Doe", distance: 0.3}
```

### **Vấn đề 4: Server không nhận được request**
**Kiểm tra Server Logs:**
```bash
# Trong terminal chạy server, bạn sẽ thấy:
🔍 Received recognition request
📁 Processing image: frame.jpg
📊 Image size: 45678 bytes
💾 Saved to: dataset/temp_abc123.jpg
🤖 Starting face recognition...
✅ Recognition result: name=John Doe, distance=0.3
🗑️ Cleaned up: dataset/temp_abc123.jpg
```

## 🛠️ **Bước 3: Test API trực tiếp**

### **Test Recognition API:**
```bash
# Tạo hình ảnh test
cd f:\face-recognition
python -c "
import requests
import numpy as np
from PIL import Image
import io

# Tạo ảnh test
img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
img_bytes = io.BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

files = {'image': ('test.jpg', img_bytes, 'image/jpeg')}
response = requests.post('http://localhost:5000/api/face/recognize', files=files)
print('Response:', response.json())
"
```

### **Test Debug API:**
```bash
curl http://localhost:5000/api/face/debug
```

## 📋 **Bước 4: Checklist Debug**

- [ ] Server đang chạy (`http://localhost:5000/health` → 200 OK)
- [ ] FAISS index tồn tại (`/api/face/debug` → exists/exists)
- [ ] Có faces đã đăng ký (`/api/face/persons` → có data)
- [ ] Console không có lỗi JavaScript
- [ ] Server logs hiển thị recognition requests
- [ ] Camera có thể capture frames
- [ ] Canvas.toBlob() hoạt động (blob size > 0)

## 🎯 **Bước 5: Troubleshooting nâng cao**

### **Nếu vẫn không hoạt động:**

1. **Check Browser Console:**
   - Mở F12 → Console
   - Click "🔧 Debug"
   - Xem có lỗi nào không

2. **Check Server Logs:**
   - Trong terminal chạy server
   - Xem có logs recognition requests không

3. **Test với Smart Camera:**
   - Thử `http://localhost:5000/smart-camera`
   - Xem có hoạt động không

4. **Reset System:**
```bash
cd f:\face-recognition
python reset_db.py
python -c "
from embeddings import add_embedding
from database import SessionLocal
from models import Person

# Add test person
session = SessionLocal()
person = Person(name='Test Person')
session.add(person)
session.commit()

# Add embedding (you'll need to add actual image)
print('Added test person with ID:', person.id)
"
```

## 📞 **Nếu vẫn gặp vấn đề:**

1. **Chạy Debug** để lấy thông tin chi tiết
2. **Check Console** để xem error messages
3. **Kiểm tra Server Logs** trong terminal
4. **Test API trực tiếp** với curl hoặc Python

**Chúc bạn debug thành công! 🎉**
