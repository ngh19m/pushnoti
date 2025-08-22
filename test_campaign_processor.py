#!/usr/bin/env python3
"""
Script test để kiểm tra campaign processor
"""

import sys
import os
import pandas as pd

# Thêm path để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csv_reading():
    """Test đọc file CSV"""
    print("🧪 Testing CSV reading...")
    
    # Test MongoDB campaign CSV
    mongodb_file = "/home/anhnq/ai_agent_push_noti/heyj-ai-push-noti-develop/mongodb_campaign.csv"
    try:
        df_mongo = pd.read_csv(mongodb_file)
        print(f"✅ MongoDB campaign CSV: {len(df_mongo)} rows")
        
        # Tìm Scheduled campaigns
        Scheduled = df_mongo[df_mongo['status'] == 'Scheduled']
        print(f"📋 Scheduled campaigns: {len(Scheduled)}")
        
        for idx, row in Scheduled.iterrows():
            print(f"  - ID: {row['_id']}")
            print(f"    Segment: {row['segment']}")
            print(f"    Platform: {row['platform']}")
            print(f"    Language: {row['language']}")
            print(f"    Message: {row['message'][:50]}...")
        
    except Exception as e:
        print(f"❌ Error reading MongoDB CSV: {e}")
    
    # Test HeyJapan data CSV
    heyjapan_file = "/home/anhnq/ai_agent_push_noti/heyj-ai-push-noti-develop/heyjapan_noti_20250807_20250811_v2.csv"
    try:
        # Đọc một phần file để test
        df_heyj = pd.read_csv(heyjapan_file, nrows=1000)
        print(f"✅ HeyJapan data CSV (sample): {len(df_heyj)} rows")
        
        # Kiểm tra platforms
        platforms = df_heyj['platform'].unique()
        print(f"📱 Platforms found: {platforms}")
        
        # Kiểm tra languages
        languages = df_heyj['language'].unique()[:10]  # Top 10
        print(f"🌍 Languages (top 10): {languages}")
        
        # Kiểm tra segments nếu có
        if 'segment' in df_heyj.columns:
            segments = df_heyj['segment'].unique()
            print(f"🎯 Segments: {segments}")
        else:
            print("⚠️ No 'segment' column found in HeyJapan data")
        
        # Test filter theo platform Android
        android_users = df_heyj[df_heyj['platform'] == 'ANDROID']
        print(f"🤖 Android users (sample): {len(android_users)}")
        
    except Exception as e:
        print(f"❌ Error reading HeyJapan CSV: {e}")

def test_matching_logic():
    """Test logic matching giữa campaigns và users"""
    print("\n🔍 Testing matching logic...")
    
    try:
        # Sample campaign
        campaign = {
            'segment': 'Churned_subcribers',
            'platform': 'Android',
            'language': 'th'
        }
        
        # Sample users data (tạo fake data để test)
        users_data = pd.DataFrame({
            'user_pseudo_id': ['user1', 'user2', 'user3', 'user4'],
            'platform': ['ANDROID', 'ANDROID', 'IOS', 'ANDROID'],
            'language': ['th-th', 'en-us', 'th-th', 'vi-vn'],
            'segment': ['Churned_subcribers', 'Active', 'Churned_subcribers', 'Churned_subcribers']
        })
        
        print(f"📊 Sample users data:")
        print(users_data)
        
        # Test matching
        platform_mapping = {
            'Android': 'ANDROID',
            'IOS': 'IOS',
            'iOS': 'IOS'
        }
        mapped_platform = platform_mapping.get(campaign['platform'], campaign['platform'].upper())
        
        # Filter by platform
        filtered = users_data[users_data['platform'] == mapped_platform]
        print(f"\n🤖 After platform filter ({mapped_platform}): {len(filtered)} users")
        
        # Filter by segment
        if 'segment' in users_data.columns:
            filtered = filtered[filtered['segment'] == campaign['segment']]
            print(f"🎯 After segment filter ({campaign['segment']}): {len(filtered)} users")
        
        # Filter by language
        language_variants = [
            campaign['language'],
            campaign['language'].lower(),
            f"{campaign['language'].lower()}-{campaign['language'].lower()}",
            f"{campaign['language'].lower()}-us",
            f"{campaign['language'].lower()}-gb"
        ]
        
        if 'language' in users_data.columns:
            filtered = filtered[filtered['language'].isin(language_variants)]
            print(f"🌍 After language filter ({campaign['language']}): {len(filtered)} users")
        
        matching_users = filtered['user_pseudo_id'].tolist()
        print(f"✅ Final matching users: {matching_users}")
        
    except Exception as e:
        print(f"❌ Error in matching logic: {e}")

if __name__ == "__main__":
    print("🧪 Campaign Processor Test")
    print("=" * 50)
    
    test_csv_reading()
    test_matching_logic()
    
    print("\n✅ Test completed!")
