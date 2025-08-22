#!/usr/bin/env python3
"""
Script để xử lý campaigns có status 'Scheduled'
Lấy dữ liệu từ MongoDB hoặc CSV, tìm FCM tokens phù hợp và gửi lên Kafka topic "push-ready"

Cách sử dụng:
# Gửi lên Kafka topic "push-ready"
python run_campaign_processor.py --source mongodb --kafka-topic push-ready

# Gửi lên Kafka topic khác
python run_campaign_processor.py --source mongodb --kafka-topic custom-topic

# Dry-run để xem trước
python run_campaign_processor.py --source mongodb --dry-run
"""

import sys
import os
import argparse
import pandas as pd

# Thêm path để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.campaign_processor import CampaignProcessor
from app.core.service_init import init_services
from app.core.logger import logger

def main():
    parser = argparse.ArgumentParser(description='Campaign Processor for Scheduled campaigns')
    parser.add_argument('--source', choices=['csv', 'mongodb'], default='csv',
                       help='Nguồn dữ liệu campaigns (csv hoặc mongodb)')
    parser.add_argument('--kafka-topic', default='push-ready',
                       help='Kafka topic để gửi dữ liệu')
    parser.add_argument('--collection-name', default='test',
                       help='Tên collection MongoDB chứa campaigns')
    parser.add_argument('--dry-run', action='store_true',
                       help='Chạy thử không gửi lên Kafka')
    
    args = parser.parse_args()
    
    try:
        # Khởi tạo services
        logger.info("🚀 Khởi tạo services...")
        init_services()
        
        # Tạo processor
        processor = CampaignProcessor()
        
        if args.dry_run:
            logger.info("🧪 Chế độ dry-run: Sẽ không gửi dữ liệu lên Kafka")
            
            # Lấy campaigns
            if args.source == 'mongodb':
                campaigns = processor.get_Scheduled_campaigns_from_mongodb()
            else:
                campaigns = processor.get_Scheduled_campaigns_from_csv()
            
            if not campaigns:
                logger.warning("Không tìm thấy campaigns nào có status 'Scheduled'")
                return
            
            # Xem trước dữ liệu
            for campaign in campaigns:
                segment = campaign.get('segment', '')
                platform = campaign.get('platform', '')
                language = campaign.get('language', '')
                country = campaign.get('country', '')
                message = campaign.get('message', '')
                
                logger.info(f"Campaign ID: {campaign.get('_id', 'N/A')}")
                logger.info(f"  Segment: {segment}")
                logger.info(f"  Platform: {platform}")
                logger.info(f"  Language: {language}")
                logger.info(f"  Country: {country}")
                logger.info(f"  Message: {message[:50]}...")
                
                # Lấy một số FCM tokens để xem trước
                fcm_tokens = processor.get_fcm_tokens_by_segment_platform(segment, platform, language, country)
                logger.info(f"  Tìm thấy {len(fcm_tokens)} FCM tokens")
                
                if fcm_tokens:
                    logger.info(f"  Sample tokens: {fcm_tokens[:3]}...")
                    # Preview format Kafka message
                    preview_payload = {
                        "message": message,
                        "tokens": fcm_tokens[:3]  # Chỉ show 3 tokens đầu
                    }
                    logger.info(f"  Kafka payload preview: {preview_payload}")
                logger.info("-" * 50)
        else:
            # Chạy thật - gửi lên Kafka
            use_mongodb = (args.source == 'mongodb')
            processor.process_Scheduled_campaigns(
                use_mongodb=use_mongodb, 
                kafka_topic=args.kafka_topic,
                collection_name=args.collection_name
            )
        
    except Exception as e:
        logger.error(f"❌ Lỗi: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
