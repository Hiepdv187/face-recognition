# Dùng Python 3.10
FROM python:3.10-slim

# Cài gói cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục app
WORKDIR /app

# Copy code
COPY . /app

# Cài dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục data
RUN mkdir -p /app/dataset /app/embeddings

# Chạy bằng Gunicorn (4 worker)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
