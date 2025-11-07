#!/usr/bin/env python3
"""
MySQL Connection Test for Producer
Quick diagnostic tool to verify MySQL connectivity
"""

import sys
import os
import json
import mysql.connector
from mysql.connector import Error

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_mysql_connection():
    """Test MySQL connection using config.json settings"""
    
    # Load config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config.json: {e}")
        return False
    
    mysql_config = config.get('mysql', {})
    host = mysql_config.get('host', 'localhost')
    port = mysql_config.get('port', 3306)
    database = mysql_config.get('database', 'kafka_stream')
    user = mysql_config.get('user', 'kafka_user')
    password = mysql_config.get('password', 'kafka_password')
    
    print("=" * 60)
    print("🔍 MySQL Connection Test for Producer")
    print("=" * 60)
    print(f"Host:     {host}")
    print(f"Port:     {port}")
    print(f"Database: {database}")
    print(f"User:     {user}")
    print("-" * 60)
    
    # Test 1: Basic connection
    print("\n[Test 1] Testing basic connection...")
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=5
        )
        print("✅ Connection successful!")
        
        # Test 2: Query test
        print("\n[Test 2] Testing query execution...")
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL Version: {version[0]}")
        
        # Test 3: Check topics table
        print("\n[Test 3] Checking topics table...")
        cursor.execute("SELECT COUNT(*) FROM topics")
        count = cursor.fetchone()
        print(f"✅ Topics in database: {count[0]}")
        
        # Test 4: List active topics
        print("\n[Test 4] Listing active topics...")
        cursor.execute("SELECT name, status FROM topics WHERE status='active'")
        topics = cursor.fetchall()
        if topics:
            print(f"✅ Active topics ({len(topics)}):")
            for name, status in topics:
                print(f"   - {name} ({status})")
        else:
            print("⚠️  No active topics found")
        
        # Test 5: List all topics
        print("\n[Test 5] Listing all topics...")
        cursor.execute("SELECT name, status FROM topics")
        all_topics = cursor.fetchall()
        if all_topics:
            print(f"✅ All topics ({len(all_topics)}):")
            for name, status in all_topics:
                print(f"   - {name} ({status})")
        else:
            print("⚠️  No topics found in database")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except Error as e:
        print(f"\n❌ MySQL Error: {e}")
        print(f"   Error Code: {e.errno}")
        print(f"   SQL State: {e.sqlstate}")
        print("\n" + "=" * 60)
        print("❌ Connection failed!")
        print("=" * 60)
        print("\n🔧 Troubleshooting steps:")
        print(f"1. Check if MySQL is running on {host}")
        print(f"2. Verify host IP address is correct: {host}")
        print(f"3. Test network connectivity: ping {host}")
        print(f"4. Test port access: nc -zv {host} {port}")
        print(f"5. Check MySQL grants for user '{user}' from this IP")
        print(f"6. Review firewall rules on both systems")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("\n" + "=" * 60)
        print("❌ Connection failed!")
        print("=" * 60)
        return False

def test_multiple_connections(num_tests=5):
    """Test multiple connections to detect intermittent issues"""
    
    print("\n" + "=" * 60)
    print(f"🔄 Testing {num_tests} consecutive connections...")
    print("=" * 60)
    
    # Load config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    mysql_config = config.get('mysql', {})
    
    success = 0
    failed = 0
    
    for i in range(1, num_tests + 1):
        print(f"\n[Connection {i}/{num_tests}]", end=" ")
        try:
            conn = mysql.connector.connect(
                host=mysql_config.get('host', 'localhost'),
                port=mysql_config.get('port', 3306),
                user=mysql_config.get('user', 'kafka_user'),
                password=mysql_config.get('password', 'kafka_password'),
                database=mysql_config.get('database', 'kafka_stream'),
                connection_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            print("✅ Success")
            success += 1
        except Error as e:
            print(f"❌ Failed - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Failed - {e}")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Results: {success} success, {failed} failed")
    
    if failed > 0:
        print("⚠️  Network instability detected!")
        print("   Consider checking:")
        print("   - Network stability (ping test)")
        print("   - Firewall rules")
        print("   - MySQL max_connections")
    else:
        print("✅ All connections stable")
    
    print("=" * 60)

if __name__ == "__main__":
    import time
    
    # Run basic test
    success = test_mysql_connection()
    
    # If successful, offer to run stability test
    if success:
        print("\n")
        response = input("Run stability test (5 connections)? [y/N]: ")
        if response.lower() == 'y':
            test_multiple_connections(5)
