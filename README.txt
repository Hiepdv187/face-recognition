HỆ THỐNG NHẬN DIỆN KHUÔN MẶT

Đây là hệ thống nhận diện khuôn mặt sử dụng Deep Learning, được đóng gói trong Docker để dễ dàng triển khai.

1. YÊU CẦU HỆ THỐNG
- Docker và Docker Compose đã được cài đặt
- Tối thiểu 4GB RAM
- Kết nối Internet để tải các mô hình

2. CẤU TRÚC THƯ MỤC
- /dataset: Chứa ảnh khuôn mặt đã đăng ký
- /embeddings: Lưu trữ các vector đặc trưng của khuôn mặt
- /models: Chứa các mô hình nhận diện
- /nginx: Cấu hình Nginx
- /samples: Chứa ảnh mẫu để test
- /uploads: Thư mục tạm để upload ảnh

3. CÀI ĐẶT VÀ KHỞI CHẠY

Cách 1: Sử dụng Docker (Khuyến nghị)
1. Đảm bảo Docker và Docker Compose đã được cài đặt
2. Mở terminal và chạy lệnh:
   docker-compose up --build
3. Hệ thống sẽ khởi động và chạy trên http://localhost

Cách 2: Cài đặt trực tiếp
1. Tạo môi trường ảo Python:
   python -m venv venv
   .\venv\Scripts\activate

2. Cài đặt các thư viện cần thiết:
   pip install -r requirements.txt

3. Khởi động ứng dụng:
   python -3 app_realtime.py

4. Ứng dụng sẽ chạy trên http://localhost:5000

4. API ENDPOINTS

- Đăng ký khuôn mặt mới:
  POST /face-register
  Form data:
    - name: Tên người dùng
    - file: Ảnh chứa khuôn mặt

- Nhận diện khuôn mặt:
  POST /face-recognition
  Form data:
    - file: Ảnh cần nhận diện

5. HƯỚNG DẪN SỬ DỤNG

1. Đăng ký khuôn mặt:
   - Gửi POST request đến /face-register với tên và ảnh khuôn mặt
   - Hệ thống sẽ lưu ảnh và tạo vector đặc trưng

2. Nhận diện khuôn mặt:
   - Gửi POST request đến /face-recognition với ảnh cần nhận diện
   - Hệ thống sẽ trả về tên người nếu nhận diện được

6. LƯU Ý
- Ảnh đăng ký nên rõ nét, chụp chính diện khuôn mặt
- Đảm bảo đủ ánh sáng khi chụp ảnh
- Mỗi người nên đăng ký nhiều ảnh với các góc độ khác nhau để tăng độ chính xác

7. TROUBLESHOOTING
- Nếu gặp lỗi về thư viện, thử cài đặt lại requirements.txt
- Kiểm tra dung lượng ổ đĩa nếu gặp lỗi lưu trữ
- Xóa file face_recognition.db nếu cần reset cơ sở dữ liệu