# Campaign Processor - Push Notification System

## Mô tả

System này thực hiện các chức năng sau:

1. **Lấy dữ liệu campaigns** từ MongoDB hoặc file CSV với status "Scheduled"
2. **Tìm kiếm FCM tokens** từ file dữ liệu HeyJapan phù hợp với segment và platform của campaign
3. **Gửi dữ liệu lên Kafka topic "push-ready"** với format mới
4. **Cập nhật status campaigns thành "push-ready"** sau khi publish thành công

## Cấu trúc Files

```
app/
├── services/
│   ├── campaign_processor.py    # Logic xử lý campaigns
│   ├── kafka_service.py        # Service gửi dữ liệu lên Kafka
│   └── mongo_service.py        # Service kết nối MongoDB
├── api/
│   └── campaign.py             # API endpoints cho campaigns
└── core/
    ├── service_init.py         # Khởi tạo services
    └── config.py               # Configuration

Scripts:
├── run_campaign_processor.py   # Script chính để chạy xử lý
├── kafka_consumer.py          # Script để đọc dữ liệu từ Kafka
└── test_campaign_processor.py # Script test
```

## Cách sử dụng

### 1. Chạy Campaign Processor

#### Chế độ dry-run (xem trước không gửi lên Kafka):
```bash
python run_campaign_processor.py --source mongodb --dry-run
```

#### Chạy thật gửi lên Kafka topic "push-ready":
```bash
python run_campaign_processor.py --source mongodb --kafka-topic push-ready
```

#### Gửi lên Kafka topic khác:
```bash
python run_campaign_processor.py --source mongodb --kafka-topic custom-topic
```

#### Lấy dữ liệu từ CSV thay vì MongoDB:
```bash
python run_campaign_processor.py --source csv --kafka-topic push-ready
```

### 2. Kiểm tra dữ liệu trên Kafka

```bash
python kafka_consumer.py --topic push-ready --max-messages 10
```

### 3. API Endpoints

Khởi động server:
```bash
python app/main.py
```

Endpoints có sẵn:
- `POST /api/campaign/process-scheduling-campaigns` - Xử lý campaigns scheduling
- `GET /api/campaign/scheduling-campaigns` - Lấy danh sách campaigns scheduling  
- `POST /api/campaign/get-users-by-segment-platform` - Lấy users theo segment/platform

## Input Data

### MongoDB Campaign CSV Format
```csv
_id,message,segment,start_time,status,label,platform,language,android,country,ios
689c54f3daa2c29236591161,Message content,Churned_subcribers,2025-08-13T09:03:40.501Z,Scheduling,sale,Android,th,,,
```

### HeyJapan Data CSV Format  
```csv
user_pseudo_id,event_date,platform,language,country,user_id,is_premium,segment,fcm_token
00a0aaa08b1eb107a4adc3cc1ca3dbab,2025-08-09,ANDROID,en-us,Philippines,3417156,,,"fcm_token_example_123"
```

## Output Data (Kafka Message)

```json
{
  "message": "🎯 ปิดท้ายซัมเมอร์ให้สุดปัง!...",
  "tokens": ["fcm_token_1", "fcm_token_2", "fcm_token_3"]
}
```

## Matching Logic

System sẽ match campaigns với users dựa trên:

1. **Platform**: Android ↔ ANDROID, IOS ↔ IOS
2. **Segment**: Xử lý các biến thể tên segment (underscore vs space)
   - "Churned_subcribers" ↔ "Churned Subcribers"
   - "Churned subcribers" ↔ "Churned_subcribers"
3. **Language**: Match 2 ký tự đầu (ko ↔ ko-kr, vi ↔ vi-vn)
4. **FCM Tokens**: Lấy từ column `fcm_token` hoặc tạo mock token từ `user_pseudo_id`

## Workflow

1. **Trigger**: Khi có trigger từ hệ thống
2. **Load Campaigns**: Lấy campaigns với status "Scheduled" từ MongoDB
3. **Platform Split**: Tách campaigns có nhiều platform thành riêng biệt  
4. **Find Tokens**: So sánh với dữ liệu HeyJapan để lấy FCM tokens
5. **Kafka Publish**: Gửi lên topic "push-ready" với format `{"message": "...", "tokens": [...]}`
6. **Update Status**: Cập nhật status campaigns thành "push-ready"

## Configuration

Cấu hình trong `app/core/config.py`:
- MongoDB URI
- Kafka Bootstrap Servers  
- Firebase Service Account

## Dependencies

```
pandas
pymongo
confluent-kafka
fastapi
uvicorn
firebase-admin
```

## Kết quả Test

✅ Đã test thành công với data thật:
- **Campaign ID**: 689c54f3daa2c29236591161 (status: Scheduled)
- **Segment**: Churned Subcribers  
- **Platform**: Android
- **Tìm thấy**: 2 FCM tokens phù hợp
- **Kafka Topic**: push-ready
- **Format**: `{"message": "...", "tokens": ["token1", "token2"]}`
- **Status**: Đã gửi thành công lên Kafka và cập nhật campaign status thành "push-ready"
