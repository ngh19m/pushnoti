#!/usr/bin/env python3
"""
Script để đọc và kiểm tra dữ liệu từ Kafka topic
"""

import sys
import os
import json
from confluent_kafka import Consumer, KafkaException
import signal

# Thêm path để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logger import logger

def create_consumer(topic: str, group_id: str = "campaign_consumer"):
    """Tạo Kafka consumer"""
    config = {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
        'group.id': group_id,
        'auto.offset.reset': 'earliest',  # Đọc từ đầu topic
        'enable.auto.commit': True
    }
    
    consumer = Consumer(config)
    consumer.subscribe([topic])
    return consumer

def consume_messages(topic: str, max_messages: int = 10):
    """Đọc messages từ Kafka topic"""
    consumer = create_consumer(topic)
    messages_consumed = 0
    
    try:
        logger.info(f"🔍 Đang đọc messages từ topic: {topic}")
        logger.info(f"📊 Tối đa {max_messages} messages")
        logger.info("Press Ctrl+C để dừng...\n")
        
        while messages_consumed < max_messages:
            msg = consumer.poll(timeout=2.0)
            
            if msg is None:
                logger.info("⏳ Không có message mới...")
                continue
            
            if msg.error():
                logger.error(f"❌ Consumer error: {msg.error()}")
                continue
            
            # Decode message
            try:
                message_value = msg.value().decode('utf-8')
                message_data = json.loads(message_value)
                
                messages_consumed += 1
                logger.info(f"📨 Message {messages_consumed}:")
                logger.info(f"  🆔 Campaign ID: {message_data.get('campaign_id', 'N/A')}")
                logger.info(f"  📝 Message: {message_data.get('message', 'N/A')[:100]}...")
                logger.info(f"  🎯 Segment: {message_data.get('segment', 'N/A')}")
                logger.info(f"  📱 Platform: {message_data.get('platform', 'N/A')}")
                logger.info(f"  🌍 Language: {message_data.get('language', 'N/A')}")
                logger.info(f"  👥 User Count: {message_data.get('user_count', 0)}")
                logger.info(f"  ⏰ Processed At: {message_data.get('processed_at', 'N/A')}")
                
                # Hiển thị một vài user_pseudo_id đầu tiên
                user_ids = message_data.get('user_pseudo_ids', [])
                if user_ids:
                    sample_users = user_ids[:5]
                    logger.info(f"  👤 Sample Users: {sample_users}")
                    if len(user_ids) > 5:
                        logger.info(f"  ... và {len(user_ids) - 5} users khác")
                
                logger.info("-" * 70)
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Lỗi decode JSON: {e}")
                logger.info(f"Raw message: {message_value}")
            except Exception as e:
                logger.error(f"❌ Lỗi xử lý message: {e}")
        
        logger.info(f"✅ Đã đọc {messages_consumed} messages thành công")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Đã dừng consumer")
    except Exception as e:
        logger.error(f"❌ Lỗi consumer: {e}")
    finally:
        consumer.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka Message Consumer')
    parser.add_argument('--topic', default='campaign_users',
                       help='Kafka topic để đọc')
    parser.add_argument('--max-messages', type=int, default=10,
                       help='Số lượng messages tối đa để đọc')
    parser.add_argument('--group-id', default='campaign_consumer',
                       help='Consumer group ID')
    
    args = parser.parse_args()
    
    logger.info("🚀 Kafka Consumer Starting...")
    consume_messages(args.topic, args.max_messages)

if __name__ == "__main__":
    main()
