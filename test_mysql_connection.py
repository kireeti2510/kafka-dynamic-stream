#!/usr/bin/env python3
"""
MySQL Connection Tester
Tests MySQL connectivity with detailed diagnostics
"""

import mysql.connector
import time
import sys

def test_mysql_connection(host, port, user, password, database, num_tests=5):
    """
    Test MySQL connection multiple times to detect intermittent issues.
    
    Args:
        host (str): MySQL host
        port (int): MySQL port
        user (str): MySQL user
        password (str): MySQL password
        database (str): Database name
        num_tests (int): Number of connection attempts
    """
    print(f"🔍 Testing MySQL Connection")
    print(f"   Host: {host}:{port}")
    print(f"   User: {user}")
    print(f"   Database: {database}")
    print(f"   Tests: {num_tests}")
    print("=" * 60)
    
    success_count = 0
    failure_count = 0
    timings = []
    
    for i in range(1, num_tests + 1):
        print(f"\n[Test {i}/{num_tests}]")
        start_time = time.time()
        
        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=5
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            elapsed = time.time() - start_time
            timings.append(elapsed)
            
            print(f"  ✅ SUCCESS in {elapsed:.3f}s")
            success_count += 1
            
        except mysql.connector.Error as e:
            elapsed = time.time() - start_time
            print(f"  ❌ FAILED in {elapsed:.3f}s")
            print(f"     Error: {e}")
            failure_count += 1
        
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"  ❌ FAILED in {elapsed:.3f}s")
            print(f"     Unexpected error: {e}")
            failure_count += 1
        
        # Small delay between tests
        if i < num_tests:
            time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print(f"   Success: {success_count}/{num_tests} ({success_count/num_tests*100:.1f}%)")
    print(f"   Failure: {failure_count}/{num_tests} ({failure_count/num_tests*100:.1f}%)")
    
    if timings:
        avg_time = sum(timings) / len(timings)
        min_time = min(timings)
        max_time = max(timings)
        print(f"   Avg time: {avg_time:.3f}s")
        print(f"   Min time: {min_time:.3f}s")
        print(f"   Max time: {max_time:.3f}s")
    
    if failure_count > 0:
        print("\n⚠️  Network instability detected!")
        print("   Possible causes:")
        print("   - Firewall dropping packets")
        print("   - Network congestion")
        print("   - MySQL max_connections limit")
        print("   - Network interface issues")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

if __name__ == "__main__":
    import json
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        sys.exit(1)
    
    mysql_config = config.get('mysql', {})
    host = mysql_config.get('host', 'localhost')
    port = mysql_config.get('port', 3306)
    user = mysql_config.get('user', 'kafka_user')
    password = mysql_config.get('password', 'kafka_password')
    database = mysql_config.get('database', 'kafka_stream')
    
    # Allow override from command line
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        num_tests = int(sys.argv[2])
    else:
        num_tests = 10
    
    success = test_mysql_connection(host, port, user, password, database, num_tests)
    sys.exit(0 if success else 1)
