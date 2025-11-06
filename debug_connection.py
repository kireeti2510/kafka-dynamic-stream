#!/usr/bin/env python3
"""
Debug script to check Producer-Admin database connection
Run this on both Producer and Admin systems to verify they're using the same database
"""

import os
import sys
import json
import sqlite3

def check_database_connection():
    """Check database connection and display all topics"""
    
    print("="*70)
    print("DATABASE CONNECTION CHECKER")
    print("="*70)
    
    # Step 1: Check config file
    print("\n1️⃣  Checking configuration file...")
    
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"❌ config.json not found in current directory")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Please run this from the kafka_dynamic_stream directory")
        return False
    
    print(f"✓ Found config.json")
    
    # Read config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    db_path = config.get('db_path', 'topics.db')
    print(f"✓ Database path from config: {db_path}")
    
    # Step 2: Check if database file exists
    print(f"\n2️⃣  Checking database file...")
    
    if not os.path.exists(db_path):
        print(f"❌ Database file NOT found at: {db_path}")
        
        # Check if it's an NFS mount issue
        if db_path.startswith('/mnt/shared_db'):
            print(f"\n   This looks like an NFS mount path.")
            print(f"   Checking if directory is mounted...")
            
            mount_point = '/mnt/shared_db'
            if os.path.exists(mount_point):
                files = os.listdir(mount_point)
                print(f"   Mount point exists. Files: {files}")
                if not files:
                    print(f"   ⚠️  Mount point is EMPTY - NFS might not be mounted!")
                    print(f"\n   Try mounting:")
                    print(f"   sudo mount 192.168.191.36:/home/USERNAME/shared_db /mnt/shared_db")
            else:
                print(f"   ❌ Mount point {mount_point} doesn't exist!")
        
        return False
    
    print(f"✓ Database file exists: {db_path}")
    
    # Check file permissions
    stat_info = os.stat(db_path)
    print(f"✓ File size: {stat_info.st_size} bytes")
    print(f"✓ File permissions: {oct(stat_info.st_mode)[-3:]}")
    
    # Step 3: Connect to database
    print(f"\n3️⃣  Connecting to database...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print(f"✓ Successfully connected to database")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Step 4: Check tables exist
    print(f"\n4️⃣  Checking database schema...")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    
    print(f"✓ Found {len(table_names)} table(s): {', '.join(table_names)}")
    
    if 'topics' not in table_names:
        print(f"❌ 'topics' table missing!")
        return False
    
    if 'subscriptions' not in table_names:
        print(f"❌ 'subscriptions' table missing!")
        return False
    
    # Step 5: Display all topics
    print(f"\n5️⃣  Querying topics table...")
    
    cursor.execute("SELECT topic_name, status, created_at FROM topics ORDER BY created_at DESC")
    topics = cursor.fetchall()
    
    if not topics:
        print(f"⚠️  No topics found in database")
        print(f"   This is normal if no topics have been created yet")
    else:
        print(f"\n📋 ALL TOPICS IN DATABASE ({len(topics)} total):")
        print("-" * 70)
        print(f"{'Topic Name':<30} {'Status':<15} {'Created At':<25}")
        print("-" * 70)
        for topic_name, status, created_at in topics:
            print(f"{topic_name:<30} {status:<15} {created_at:<25}")
        print("-" * 70)
    
    # Step 6: Show pending topics specifically
    print(f"\n6️⃣  Checking for PENDING topics...")
    
    cursor.execute("SELECT topic_name, created_at FROM topics WHERE status='pending'")
    pending = cursor.fetchall()
    
    if not pending:
        print(f"✓ No pending topics (waiting for approval)")
    else:
        print(f"\n⚠️  Found {len(pending)} PENDING topic(s):")
        for topic_name, created_at in pending:
            print(f"   - {topic_name} (created: {created_at})")
    
    # Step 7: Show approved topics
    print(f"\n7️⃣  Checking for APPROVED topics...")
    
    cursor.execute("SELECT topic_name, created_at FROM topics WHERE status='approved'")
    approved = cursor.fetchall()
    
    if not approved:
        print(f"✓ No approved topics (waiting to be created in Kafka)")
    else:
        print(f"\n✓ Found {len(approved)} APPROVED topic(s):")
        for topic_name, created_at in approved:
            print(f"   - {topic_name} (approved: {created_at})")
    
    # Step 8: Show active topics
    print(f"\n8️⃣  Checking for ACTIVE topics...")
    
    cursor.execute("SELECT topic_name, created_at FROM topics WHERE status='active'")
    active = cursor.fetchall()
    
    if not active:
        print(f"✓ No active topics yet")
    else:
        print(f"\n✓ Found {len(active)} ACTIVE topic(s):")
        for topic_name, created_at in active:
            print(f"   - {topic_name} (active: {created_at})")
    
    # Close connection
    conn.close()
    
    print("\n" + "="*70)
    print("✅ DATABASE CHECK COMPLETE")
    print("="*70)
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"  Database: {db_path}")
    print(f"  Total topics: {len(topics)}")
    print(f"  Pending: {len(pending)}")
    print(f"  Approved: {len(approved)}")
    print(f"  Active: {len(active)}")
    print()
    
    return True


def check_kafka_connection():
    """Check Kafka broker connection"""
    
    print("\n" + "="*70)
    print("KAFKA BROKER CONNECTION CHECK")
    print("="*70)
    
    # Read config
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"❌ config.json not found")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    bootstrap_servers = config.get('bootstrap_servers', 'localhost:9092')
    print(f"\nKafka broker from config: {bootstrap_servers}")
    
    # Try to connect
    try:
        from kafka import KafkaAdminClient
        
        print(f"Attempting connection to {bootstrap_servers}...")
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id='debug_checker',
            request_timeout_ms=5000
        )
        
        topics = admin_client.list_topics()
        print(f"✅ Successfully connected to Kafka!")
        print(f"✓ Found {len(topics)} topic(s) in Kafka broker")
        
        if topics:
            print(f"\n📋 Topics in Kafka broker:")
            for topic in topics:
                if not topic.startswith('__'):  # Skip internal topics
                    print(f"   - {topic}")
        
        admin_client.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        print(f"\n⚠️  Make sure Kafka broker is running at {bootstrap_servers}")
        return False


if __name__ == '__main__':
    print("\n🔍 PRODUCER-ADMIN CONNECTION DEBUGGER")
    print("Run this script on both Producer and Admin systems")
    print()
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    print(f"Expected: kafka_dynamic_stream/")
    print()
    
    # Run checks
    db_ok = check_database_connection()
    kafka_ok = check_kafka_connection()
    
    print("\n" + "="*70)
    if db_ok and kafka_ok:
        print("✅ ALL CHECKS PASSED")
        print("Producer and Admin should be able to communicate!")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please fix the issues above")
    print("="*70)
    print()
