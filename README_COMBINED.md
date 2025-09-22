# 🚀 Face Recognition + Golang Combined Services

Hướng dẫn chạy hệ thống Face Recognition (Python Flask) và Golang service cùng nhau.

## 📋 Yêu cầu hệ thống

- Docker & Docker Compose
- CPU/RAM tối thiểu: 4GB RAM, 2 CPU cores
- Không gian đĩa: 10GB (cho dataset và embeddings)

## 🏗️ Cấu trúc hệ thống

```
📁 face-recognition/          # Python Flask Face Recognition
├── app.py                   # Main Flask application
├── config.py               # Configuration
├── database.py             # Database setup
├── models.py               # SQLAlchemy models
├── embeddings.py           # Face embedding functions
├── recognition.py          # Face recognition logic
├── requirements.txt        # Python dependencies
└── docker-compose.yml      # Combined services orchestration

📁 golang-project/           # Golang Service (create this directory)
├── main.go                 # Golang main application
├── go.mod                  # Go modules
└── Dockerfile              # Golang Docker configuration
```

## ⚡ Cách chạy nhanh

### 1. Chuẩn bị Golang project

Tạo thư mục cho Golang service:

```bash
mkdir ../golang-project
cd ../golang-project

# Tạo go.mod
go mod init golang-service

# Tạo main.go với health check endpoint
cat > main.go << 'EOF'
package main

import (
    "database/sql"
    "encoding/json"
    "log"
    "net/http"
    "os"

    _ "github.com/lib/pq"
)

type HealthResponse struct {
    Status   string `json:"status"`
    Service  string `json:"service"`
    Database string `json:"database"`
    Version  string `json:"version"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    dbURL := os.Getenv("DATABASE_URL")
    db, err := sql.Open("postgres", dbURL)
    if err != nil {
        http.Error(w, err.Error(), 500)
        return
    }
    defer db.Close()

    if err = db.Ping(); err != nil {
        http.Error(w, err.Error(), 500)
        return
    }

    response := HealthResponse{
        Status:   "healthy",
        Service:  "golang-service",
        Database: "connected",
        Version:  "1.0.0",
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func main() {
    http.HandleFunc("/health", healthHandler)
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Golang Service is running!"))
    })

    port := os.Getenv("GO_API_PORT")
    if port == "" {
        port = "8080"
    }

    log.Printf("Server starting on port %s", port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}
EOF

# Tạo Dockerfile cho Golang
cat > Dockerfile << 'EOF'
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
CMD ["./main"]
EOF
```

### 2. Cấu hình Environment Variables

Chỉnh sửa file `.env` với thông tin database thực tế:

```bash
# Chỉnh sửa các giá trị sau
POSTGRES_DB=your_database_name
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_secure_password
```

### 3. Chạy hệ thống

```bash
# Chạy tất cả services
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps

# Xem logs
docker-compose logs -f

# Chạy health check
chmod +x health_check.sh
./health_check.sh
```

## 🌐 Truy cập hệ thống

- **Face Recognition Interface**: http://localhost
- **Face Recognition API**: http://localhost/api/face/
- **Golang Service**: http://localhost/api/go/
- **Health Check**: http://localhost/health

### API Endpoints

#### Face Recognition Service:
- `GET /` - Web interface
- `POST /face-register` - Đăng ký khuôn mặt
- `POST /face-recognition` - Nhận diện khuôn mặt
- `GET /health` - Health check

#### Golang Service:
- `GET /` - Golang service homepage
- `GET /health` - Health check
- Thêm các endpoints khác theo nhu cầu

## 🛠️ Quản lý hệ thống

### Khởi động lại service
```bash
# Restart một service cụ thể
docker-compose restart face-recognition
docker-compose restart golang-service

# Restart tất cả
docker-compose restart
```

### Xem logs
```bash
# Logs của tất cả services
docker-compose logs -f

# Logs của service cụ thể
docker-compose logs -f face-recognition
docker-compose logs -f golang-service
```

### Dừng hệ thống
```bash
# Dừng tất cả services
docker-compose down

# Dừng và xóa volumes (bao gồm database)
docker-compose down -v
```

## 🔧 Troubleshooting

### Service không khởi động được
```bash
# Kiểm tra logs chi tiết
docker-compose logs [service-name]

# Test kết nối database
docker exec -it shared_postgres psql -U app_user -d face_recognition_app
```

### Port bị conflict
Chỉnh sửa `docker-compose.yml` để thay đổi ports:
```yaml
services:
  face-recognition:
    ports:
      - "5001:5000"  # Thay đổi port bên ngoài

  golang-service:
    ports:
      - "8081:8080"  # Thay đổi port bên ngoài
```

### Thêm dependencies cho Python
Chỉnh sửa `requirements.txt` và rebuild:
```bash
docker-compose build face-recognition
docker-compose up -d face-recognition
```

## 📊 Monitoring

- **Health Checks**: Tự động check mỗi 30 giây
- **Logs**: Xem qua `docker-compose logs`
- **Resource Usage**: `docker stats`
- **Database**: Truy cập trực tiếp qua port 5432

## 🚀 Development Mode

Để chạy trong môi trường development:

```bash
# Chạy không có daemon mode để xem logs
docker-compose up

# Hoặc chạy từng service riêng
docker-compose up postgres
docker-compose up face-recognition
docker-compose up golang-service
```

## 📝 Lưu ý quan trọng

1. **Database**: Mặc định sử dụng PostgreSQL, có thể chuyển về SQLite bằng cách thay đổi `DATABASE_URL`
2. **Volumes**: Dữ liệu được lưu trong Docker volumes, persistent giữa các lần chạy
3. **Security**: Thay đổi password trong file `.env` trước khi production
4. **Backup**: Database data được lưu trong volume `postgres_data`

## 🆘 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Docker và Docker Compose đã cài đặt
2. Ports không bị chiếm dụng
3. File `.env` có thông tin database chính xác
4. Logs của từng service

Chạy `docker-compose logs -f` để xem logs chi tiết.
