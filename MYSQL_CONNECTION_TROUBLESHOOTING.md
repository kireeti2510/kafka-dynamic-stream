# MySQL Connection Issues - Troubleshooting Guide

## Problem
Producer showing intermittent MySQL connection failures:
```
✗ Error connecting to MySQL database: 2003 (HY000): Can't connect to MySQL server on '192.168.191.183:3306' (113)
```

Error 113 = "No route to host" - Network connectivity issue

## System Architecture
- **Admin/MySQL**: 192.168.191.183 (macOS)
- **Kafka Broker**: 192.168.191.169 (Ubuntu)
- **Producer**: 192.168.191.169 (Ubuntu)
- **Consumer**: Other systems

## Root Causes

### 1. Network Instability
The connection succeeds sometimes and fails other times, indicating:
- Packet loss on network
- Firewall intermittently blocking connections
- Network interface issues
- ARP cache problems

### 2. MySQL Connection Pool Exhaustion
- Too many connections being opened
- Not properly closing connections
- Hitting max_connections limit

### 3. Firewall/Network Issues
- macOS firewall blocking some packets
- Network switch/router issues
- WiFi instability (if using wireless)

## Solutions

### Solution 1: Test Network Stability

**On Producer system (192.168.191.169)**, run:

```bash
# Test 1: Continuous ping
ping -c 100 192.168.191.183

# Test 2: Check for packet loss
ping -i 0.2 -c 100 192.168.191.183 | tail -3

# Test 3: Test MySQL port continuously
for i in {1..20}; do
  echo "Test $i:"
  nc -zv -w 2 192.168.191.183 3306
  sleep 0.5
done

# Test 4: MySQL connection test
mysql -h 192.168.191.183 -u kafka_user -pkafka_password -e "SELECT 1;" && echo "SUCCESS" || echo "FAILED"
```

### Solution 2: Check MySQL Server Status

**On Admin system (192.168.191.183 - macOS)**, run:

```bash
# Check MySQL status
mysql -u root -p -e "SHOW STATUS LIKE 'Threads_connected';"
mysql -u root -p -e "SHOW STATUS LIKE 'Max_used_connections';"
mysql -u root -p -e "SHOW VARIABLES LIKE 'max_connections';"

# Check for connection errors
mysql -u root -p -e "SHOW STATUS LIKE 'Aborted_connects';"
mysql -u root -p -e "SHOW STATUS LIKE 'Connection_errors%';"
```

### Solution 3: Increase MySQL Connection Limits

**On Admin system**, edit MySQL config:

```bash
# Edit MySQL config
nano /opt/homebrew/etc/my.cnf

# Add these lines under [mysqld]
max_connections = 500
wait_timeout = 600
interactive_timeout = 600
connect_timeout = 10

# Restart MySQL
brew services restart mysql
```

### Solution 4: Add Connection Retry Logic

The producer should retry MySQL connections. Let me check if retry logic exists...

### Solution 5: Use Connection Pooling

Add connection pooling to reduce connection overhead:

```python
from mysql.connector import pooling

# Create connection pool (add to db_setup.py)
connection_pool = pooling.MySQLConnectionPool(
    pool_name="kafka_pool",
    pool_size=10,
    pool_reset_session=True,
    host='192.168.191.183',
    database='kafka_stream',
    user='kafka_user',
    password='kafka_password'
)
```

### Solution 6: Check Network Configuration

**On Producer system**, verify routing:

```bash
# Check route to MySQL server
ip route get 192.168.191.183

# Check ARP cache
arp -a | grep 192.168.191.183

# Clear ARP cache if needed
sudo ip -s -s neigh flush all

# Check network interface
ip addr show
```

### Solution 7: Disable macOS Network Throttling

**On Admin system (macOS)**, disable network power management:

```bash
# Check current settings
pmset -g

# Disable network power management
sudo pmset -a tcpkeepalive 1
sudo pmset -a powernap 0

# For Ethernet
sudo ifconfig en0 media autoselect
```

### Solution 8: Check Firewall Logs

**On Admin system (macOS)**:

```bash
# Check system logs for connection drops
log show --predicate 'eventMessage contains "192.168.191.169"' --last 10m

# Check firewall logs
sudo pfctl -s state | grep 3306
```

### Solution 9: Add MySQL Connection Timeout Handling

Modify producer to handle connection failures gracefully:

```python
import time
from mysql.connector import Error as MySQLError

def execute_with_retry(query_func, max_retries=3, delay=1):
    """Execute database query with retry logic"""
    for attempt in range(max_retries):
        try:
            return query_func()
        except MySQLError as e:
            if attempt < max_retries - 1:
                print(f"⚠ MySQL error (attempt {attempt+1}/{max_retries}): {e}")
                time.sleep(delay)
            else:
                raise
```

## Quick Fix: Verify Config on Producer System

**CRITICAL**: On the Producer system (192.168.191.169), verify config.json:

```json
{
  "bootstrap_servers": "localhost:9092",  // Producer is on same system as Kafka
  "mysql": {
    "host": "192.168.191.183",  // MySQL is on Admin system
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "kafka_password"
  }
}
```

## Testing Procedure

### Step 1: Run Connection Test
```bash
# On Producer system
python3 test_mysql_connection.py 192.168.191.183 20
```

### Step 2: Monitor Network
```bash
# On Producer system - monitor in real-time
watch -n 1 'nc -zv -w 1 192.168.191.183 3306 2>&1'
```

### Step 3: Check MySQL Logs
```bash
# On Admin system
tail -f /opt/homebrew/var/mysql/*.err
```

## Immediate Workaround

If network is unstable, consider:

1. **Move MySQL to Producer system** (192.168.191.169)
   - Both Producer and Broker would use localhost
   - Eliminates network issues

2. **Use different MySQL server**
   - Set up MySQL on a more stable system
   - Update all config.json files

3. **Add aggressive retry logic**
   - Retry failed MySQL operations
   - Use exponential backoff

## Expected Behavior

After fixes:
- ✅ All MySQL connections should succeed
- ✅ No intermittent failures
- ✅ Consistent performance

## Debug Commands Summary

```bash
# Network tests
ping -c 100 192.168.191.183
nc -zv 192.168.191.183 3306
traceroute 192.168.191.183

# MySQL tests
mysql -h 192.168.191.183 -u kafka_user -pkafka_password -e "SELECT 1;"

# System checks
netstat -an | grep 3306
lsof -i :3306
ss -s
