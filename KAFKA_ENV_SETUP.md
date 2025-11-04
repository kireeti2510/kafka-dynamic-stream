# Kafka Environment Setup and Validation

## Overview

The `kafka_env_setup.py` module provides comprehensive Kafka environment validation to ensure all prerequisites are met before running the Dynamic Content Stream application.

## Features

### 1️⃣ **Installation Detection**
- Verifies Kafka is installed at `/opt/kafka`
- Checks for essential binaries in `/opt/kafka/bin`
- Validates configuration files existence

### 2️⃣ **Service Status Validation**
- Detects if ZooKeeper is running
- Detects if Kafka Broker is running
- Provides start commands if services are down

### 3️⃣ **Broker Connection Testing**
- Tests connectivity to Kafka broker (default: `localhost:9092`)
- Uses `KafkaAdminClient` for validation
- Clear error messages on connection failure

### 4️⃣ **Configuration Reading**
- Reads `/opt/kafka/config/server.properties`
- Displays key configuration values:
  - `listeners`
  - `log.dirs`
  - `broker.id`
  - `num.partitions`
  - `log.retention.hours`
  - `zookeeper.connect`

### 5️⃣ **Admin API Validation** (Optional)
- Creates a test topic `__connection_check__`
- Verifies topic creation capability
- Deletes test topic after validation
- Ensures Admin API is functional

---

## Usage

### Command Line Interface

```bash
# Full validation (default)
python3 kafka_env_setup.py

# Quick connection check only
python3 kafka_env_setup.py --quick

# Custom broker address
python3 kafka_env_setup.py --broker localhost:9093

# Auto-start services if not running (experimental)
python3 kafka_env_setup.py --auto-start

# Skip Admin API validation
python3 kafka_env_setup.py --skip-admin
```

### Python API

```python
from kafka_env_setup import verify_kafka_connection

# Full validation (recommended)
verify_kafka_connection()

# Skip Admin API test
verify_kafka_connection(validate_admin=False)

# Custom broker
verify_kafka_connection(broker='localhost:9093')

# Quick check (returns True/False)
from kafka_env_setup import quick_check
if quick_check():
    print("Kafka is ready!")
```

---

## Integration

The validation is automatically integrated into:

### **Producer** (`producer/producer.py`)
```python
from kafka_env_setup import verify_kafka_connection

def main():
    # Validate before starting
    verify_kafka_connection(validate_admin=True)
    # ... rest of code
```

### **Consumer** (`consumer/consumer.py`)
```python
from kafka_env_setup import verify_kafka_connection

def main():
    # Validate before starting
    verify_kafka_connection(validate_admin=False)
    # ... rest of code
```

### **Topic Watcher** (`producer/topic_watcher.py`)
```python
# When run standalone
if __name__ == '__main__':
    verify_kafka_connection(validate_admin=True)
    # ... start watcher
```

---

## Validation Process

### Step-by-Step Flow

```
1. Check Kafka Installation
   ├── Verify /opt/kafka exists
   ├── Check /opt/kafka/bin directory
   ├── Validate critical binaries
   └── Confirm config files exist

2. Check Service Status
   ├── Search for ZooKeeper process
   ├── Search for Kafka Broker process
   └── Display start commands if needed

3. Read Server Configuration
   ├── Parse server.properties
   ├── Extract key settings
   └── Display configuration summary

4. Test Broker Connection
   ├── Create KafkaAdminClient
   ├── Attempt connection to broker
   ├── List topics to verify
   └── Close connection

5. Verify Admin API (Optional)
   ├── Create test topic
   ├── Confirm creation success
   ├── Delete test topic
   └── Validate deletion

✅ All checks passed → Application starts
❌ Any check fails → Exit with clear error
```

---

## Output Examples

### ✅ Successful Validation

```
============================================================
🔍 KAFKA ENVIRONMENT VALIDATION
============================================================

1️⃣  Checking Kafka Installation...
✓ Kafka home directory found: /opt/kafka
✓ Kafka binaries found: /opt/kafka/bin
✓ All critical binaries present (6 checked)
✓ Kafka config directory found: /opt/kafka/config
✓ ZooKeeper config found: /opt/kafka/config/zookeeper.properties
✓ Kafka server config found: /opt/kafka/config/server.properties

✅ Kafka installation validated successfully!

2️⃣  Checking Service Status...
✓ ZooKeeper is running
✓ Kafka Broker is running

✅ All Kafka services are running!

3️⃣  Reading Kafka Server Configuration...

📋 Key Configuration Values:
------------------------------------------------------------
   listeners                = PLAINTEXT://localhost:9092
   log.dirs                 = /tmp/kafka-logs
   broker.id                = 0
   num.partitions           = 1
   log.retention.hours      = 168
   zookeeper.connect        = localhost:2181
------------------------------------------------------------

4️⃣  Testing Kafka Broker Connection...
   Connecting to: localhost:9092
✓ Successfully connected to Kafka broker at localhost:9092
✓ Cluster has 3 topic(s)

5️⃣  Verifying Kafka Admin API...
   Creating test topic: __connection_check__
✓ Test topic created successfully
   Deleting test topic: __connection_check__
✓ Test topic deleted successfully

✅ Kafka Admin API is fully functional!

============================================================
✅ ALL KAFKA ENVIRONMENT CHECKS PASSED
============================================================
🚀 Ready to start Kafka-based applications!
```

### ❌ Services Not Running

```
============================================================
🔍 KAFKA ENVIRONMENT VALIDATION
============================================================

1️⃣  Checking Kafka Installation...
✓ Kafka home directory found: /opt/kafka
✓ Kafka binaries found: /opt/kafka/bin
✓ All critical binaries present (6 checked)
✓ Kafka config directory found: /opt/kafka/config
✓ ZooKeeper config found: /opt/kafka/config/zookeeper.properties
✓ Kafka server config found: /opt/kafka/config/server.properties

✅ Kafka installation validated successfully!

2️⃣  Checking Service Status...
❌ ZooKeeper is NOT running
❌ Kafka Broker is NOT running

============================================================
⚠️  KAFKA SERVICES NOT RUNNING
============================================================

📌 To start ZooKeeper:
   cd /opt/kafka
   bin/zookeeper-server-start.sh config/zookeeper.properties &
   (Or run in a separate terminal without '&')

📌 To start Kafka Broker:
   cd /opt/kafka
   bin/kafka-server-start.sh config/server.properties &
   (Or run in a separate terminal without '&')

   Note: Start ZooKeeper first, then Kafka Broker

============================================================

============================================================
❌ KAFKA ENVIRONMENT VALIDATION FAILED
============================================================
Error: Required Kafka services are not running

Please fix the issues above before proceeding.
============================================================
```

---

## Functions Reference

### `check_kafka_installation()`
Validates Kafka installation at `/opt/kafka`.

**Returns:** `bool`  
**Raises:** `KafkaEnvironmentError` if installation incomplete

### `check_services_status()`
Checks if ZooKeeper and Kafka are running.

**Returns:** `tuple (zk_running, kafka_running)`  
**Raises:** `KafkaEnvironmentError` if services not running

### `read_server_properties()`
Parses `server.properties` and extracts key settings.

**Returns:** `dict` of configuration values

### `test_broker_connection(broker='localhost:9092', timeout=10)`
Tests connectivity to Kafka broker.

**Args:**
- `broker` (str): Broker address
- `timeout` (int): Connection timeout in seconds

**Returns:** `bool`  
**Raises:** `KafkaEnvironmentError` if connection fails

### `verify_admin_api()`
Tests Admin API by creating/deleting a test topic.

**Returns:** `bool`

### `start_kafka_services(background=True)`
Programmatically starts ZooKeeper and Kafka (experimental).

**Args:**
- `background` (bool): Start as background processes

**Returns:** `tuple (zk_process, kafka_process)`

### `verify_kafka_connection(broker='localhost:9092', auto_start=False, validate_admin=True)`
**Main entry point** - runs all validation checks.

**Args:**
- `broker` (str): Broker address to test
- `auto_start` (bool): Attempt to start services if not running
- `validate_admin` (bool): Include Admin API validation

**Returns:** `bool`  
**Raises:** `KafkaEnvironmentError` and exits on failure

### `quick_check(broker='localhost:9092')`
Lightweight connection check without full validation.

**Args:**
- `broker` (str): Broker address

**Returns:** `bool`

---

## Error Handling

The module uses a custom exception:

```python
class KafkaEnvironmentError(Exception):
    """Custom exception for Kafka environment issues"""
    pass
```

When a critical check fails:
1. Clear error message is printed
2. `KafkaEnvironmentError` is raised
3. `sys.exit(1)` terminates the script
4. User is guided on how to fix the issue

---

## Auto-Start Feature (Experimental)

The module can automatically start Kafka services:

```python
verify_kafka_connection(auto_start=True)
```

**How it works:**
1. Detects services not running
2. Starts ZooKeeper using `subprocess.Popen`
3. Waits 5 seconds for ZooKeeper initialization
4. Starts Kafka Broker
5. Waits 10 seconds for Kafka initialization

**Limitations:**
- Processes run as background subprocesses
- No output capture in main terminal
- May require manual cleanup on exit
- Recommended for development only

---

## Integration Examples

### Example 1: Producer Startup
```python
# producer/producer.py
from kafka_env_setup import verify_kafka_connection

def main():
    try:
        # Full validation with Admin API check
        print("🔍 Validating Kafka environment...")
        verify_kafka_connection(validate_admin=True)
        
        # Proceed with producer initialization
        coordinator = ProducerCoordinator()
        coordinator.start()
    except SystemExit:
        # Validation failed, already printed error
        pass
```

### Example 2: Consumer Startup
```python
# consumer/consumer.py
from kafka_env_setup import verify_kafka_connection

def main():
    try:
        # Validate without Admin API (consumers don't need it)
        print("🔍 Validating Kafka environment...")
        verify_kafka_connection(validate_admin=False)
        
        # Proceed with consumer initialization
        consumer = DynamicConsumer(config, user_id)
        consumer.start()
    except SystemExit:
        pass
```

### Example 3: Custom Validation Script
```python
#!/usr/bin/env python3
from kafka_env_setup import (
    check_kafka_installation,
    check_services_status,
    test_broker_connection
)

# Custom validation workflow
try:
    check_kafka_installation()
    zk, kafka = check_services_status()
    
    if zk and kafka:
        test_broker_connection()
        print("✅ Ready to proceed!")
    else:
        print("❌ Start services first")
except Exception as e:
    print(f"Error: {e}")
```

---

## Benefits

✅ **Early Failure Detection** - Catch issues before application starts  
✅ **Clear Error Messages** - Users know exactly what's wrong  
✅ **Automated Checks** - No manual verification needed  
✅ **Graceful Exit** - Prevents cryptic Kafka errors  
✅ **Service Guidance** - Shows exact commands to start services  
✅ **Configuration Visibility** - Displays broker settings  
✅ **Admin API Test** - Ensures topic creation will work  
✅ **Reusable Module** - Can be imported anywhere  

---

## Troubleshooting

### Issue: "Kafka not installed at /opt/kafka"
**Solution:** Install Kafka to `/opt/kafka` or modify `KAFKA_HOME` in the module

### Issue: "Services not running"
**Solution:** Start ZooKeeper first, then Kafka Broker as shown in error message

### Issue: "Broker not reachable"
**Solution:** 
- Check `listeners` in `server.properties`
- Ensure firewall allows port 9092
- Verify Kafka is bound to correct interface

### Issue: "Admin API test failed"
**Solution:**
- Check `auto.create.topics.enable` setting
- Verify user permissions
- Check Kafka logs for errors

---

## Configuration

Default values can be modified at the top of `kafka_env_setup.py`:

```python
# Kafka installation paths
KAFKA_HOME = "/opt/kafka"
KAFKA_BIN = os.path.join(KAFKA_HOME, "bin")
KAFKA_CONFIG = os.path.join(KAFKA_HOME, "config")

# Default broker
DEFAULT_BROKER = "localhost:9092"
```

---

## Testing

### Test the module standalone:
```bash
# Full test
python3 kafka_env_setup.py

# Quick test
python3 kafka_env_setup.py --quick

# Test with different broker
python3 kafka_env_setup.py --broker localhost:9093
```

### Test integration:
```bash
# Should validate before starting
python3 producer/producer.py
python3 consumer/consumer.py 1
```

---

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--broker` | Specify broker address | `--broker localhost:9093` |
| `--auto-start` | Auto-start services if down | `--auto-start` |
| `--skip-admin` | Skip Admin API validation | `--skip-admin` |
| `--quick` | Quick connection check only | `--quick` |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed |
| `1` | Validation failed or services not ready |

---

## Performance

- **Full Validation:** ~2-5 seconds
- **Quick Check:** ~1 second
- **With Auto-Start:** ~15-20 seconds (service initialization time)

---

## Security Notes

- Module uses `ps -ef` to check processes
- No authentication credentials stored
- Admin API uses default security settings
- Test topic is automatically cleaned up

---

## Future Enhancements

Potential improvements:
- [ ] Support for multiple brokers
- [ ] SSL/TLS configuration validation
- [ ] SASL authentication checks
- [ ] Cluster health monitoring
- [ ] Performance benchmarking
- [ ] Docker environment detection

---

## Summary

The Kafka Environment Setup module provides:

1. ✅ Complete pre-flight validation
2. ✅ Automatic error detection
3. ✅ Clear troubleshooting guidance
4. ✅ Service status monitoring
5. ✅ Configuration transparency
6. ✅ Admin API verification
7. ✅ Seamless integration

**Result:** Robust, production-ready Kafka application startup! 🚀
