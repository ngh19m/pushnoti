# Sử dụng image Python 3.13
FROM python:3.13-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép chỉ file main.py vào container
COPY main.py .
COPY requirements-api-n8n.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements-api-n8n.txt

# Lệnh chạy khi container được start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "12000", "--reload"]
