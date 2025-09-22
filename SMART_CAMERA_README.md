# 🎥 Smart Camera Face Recognition

Hệ thống **Smart Camera** với tính năng nhận diện khuôn mặt real-time và hiển thị kết quả trực tiếp trên camera feed!

## ✨ Tính năng nổi bật

### 🎯 **Real-time Recognition với Overlay**
- ✅ **Tự động nhận diện** khi đưa mặt vào camera
- ✅ **Hiển thị tên trực tiếp** trên camera feed
- ✅ **Overlay text động** với hiệu ứng đẹp mắt
- ✅ **Tự động chụp và xử lý** không cần tương tác thủ công
- ✅ **Visual feedback** với animation và màu sắc

### 📊 **Smart Statistics**
- 📈 **Accuracy tracking** - Theo dõi độ chính xác
- 🎯 **Confidence scoring** - Điểm tin cậy real-time
- 📝 **Recognition history** - Lịch sử nhận diện
- 📊 **Performance metrics** - Thống kê hiệu suất

### 🎨 **Beautiful UI/UX**
- 🎨 **Modern design** - Giao diện hiện đại
- 📱 **Responsive** - Tương thích mobile
- 🌈 **Gradient effects** - Hiệu ứng màu sắc
- ⚡ **Smooth animations** - Chuyển động mượt mà

## 🚀 Cách sử dụng

### 1. Chạy hệ thống
```bash
cd f:\face-recognition
python app_realtime.py
```

### 2. Mở Smart Camera
**Truy cập:** http://localhost:5000/smart-camera

### 3. Sử dụng
1. **Click "Start Camera"** để bật webcam
2. **Đưa mặt vào khung hình** - Hệ thống tự động nhận diện
3. **Xem kết quả** hiển thị trực tiếp trên camera
4. **Đăng ký face mới** bằng nút "Register Face"

## 🌐 URLs

| Interface | URL | Mô tả |
|-----------|-----|--------|
| **Smart Camera** | http://localhost:5000/smart-camera | 🎥 **Camera với overlay** |
| **Real-time** | http://localhost:5000/realtime | 📹 Recognition đơn giản |
| **Webcam** | http://localhost:5000/webcam | 📹 Giao diện cơ bản |
| **Homepage** | http://localhost:5000/ | 🏠 Trang chủ |

## 🎥 Cách hoạt động

### **1. Camera Feed**
- Video stream từ webcam
- Canvas overlay để vẽ text
- Face detection area với brackets

### **2. Auto Recognition**
- **Tự động capture** mỗi 1.5 giây
- **Gửi ảnh** đến API nhận diện
- **Hiển thị kết quả** ngay lập tức

### **3. Visual Overlay**
```javascript
// Hiển thị tên trực tiếp trên camera
drawOverlayWithResult(result) {
    // ✅ Green text cho face đã biết
    // ❌ Red text cho unknown person
    // 📊 Confidence percentage
}
```

### **4. Statistics**
- **Total Recognitions** - Số lần nhận diện thành công
- **Accuracy Rate** - Tỷ lệ chính xác
- **Average Confidence** - Độ tin cậy trung bình

## 📋 Yêu cầu

- 🌐 **Web browser** với camera support
- 📷 **Webcam** (built-in hoặc external)
- 🔒 **HTTPS** (cho camera access trên một số browser)

## 🎯 Demo

1. **Mở** http://localhost:5000/smart-camera
2. **Start Camera** - Webcam sẽ bật
3. **Đưa mặt vào** - Tên sẽ hiển thị trên camera
4. **Xem stats** - Theo dõi thống kê real-time

## 🔧 Cấu hình

### **Recognition Interval**
```javascript
recognitionInterval = setInterval(() => {
    recognizeFrame();
}, 1500); // 1.5 giây
```

### **Camera Settings**
```javascript
video: {
    width: { ideal: 1280 },
    height: { ideal: 720 }
}
```

## 📱 Mobile Support

✅ **Hoạt động trên mobile** với responsive design
✅ **Touch controls** cho mobile devices
✅ **Camera access** thông qua HTTPS

## 🚨 Lưu ý

- 🔒 **HTTPS required** cho camera access
- 📱 **Mobile browsers** có thể cần HTTPS
- 🎯 **Face positioning** - Đưa mặt vào khung detection
- ⚡ **Performance** - Đảm bảo đủ ánh sáng

---

**🎉 Smart Camera đã sẵn sàng! Chỉ cần mở http://localhost:5000/smart-camera và bắt đầu sử dụng!**
