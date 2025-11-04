"""
Kafka Environment Setup and Validation Module
Checks Kafka installation, validates services, and tests connectivity.

This module provides comprehensive validation for Kafka infrastructure:
- Installation detection at /opt/kafka
- Service status verification (Zookeeper & Kafka)
- Broker connectivity testing
- Configuration file reading
- Admin API validation

Usage:
    from kafka_env_setup import verify_kafka_connection
    verify_kafka_connection()
"""

import os
import sys
import subprocess
import time
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, NoBrokersAvailable

# Kafka installation paths
KAFKA_HOME = "/opt/kafka"
KAFKA_BIN = os.path.join(KAFKA_HOME, "bin")
KAFKA_CONFIG = os.path.join(KAFKA_HOME, "config")
ZOOKEEPER_CONFIG = os.path.join(KAFKA_CONFIG, "zookeeper.properties")
SERVER_CONFIG = os.path.join(KAFKA_CONFIG, "server.properties")

# Default Kafka broker
DEFAULT_BROKER = "localhost:9092"


class KafkaEnvironmentError(Exception):
    """Custom exception for Kafka environment issues"""
    pass


def check_kafka_installation():
    """
    Check if Kafka is installed at /opt/kafka.
    
    Returns:
        bool: True if installation found, False otherwise
    
    Raises:
        KafkaEnvironmentError: If Kafka installation not found
    """
    print("\n" + "="*60)
    print("🔍 KAFKA ENVIRONMENT VALIDATION")
    print("="*60)
    
    print("\n1️⃣  Checking Kafka Installation...")
    
    # Check if Kafka home directory exists
    if not os.path.exists(KAFKA_HOME):
        print(f"❌ Kafka installation not found at: {KAFKA_HOME}")
        print(f"   Please install Apache Kafka to {KAFKA_HOME}")
        raise KafkaEnvironmentError(f"Kafka not installed at {KAFKA_HOME}")
    
    print(f"✓ Kafka home directory found: {KAFKA_HOME}")
    
    # Check if bin directory exists
    if not os.path.exists(KAFKA_BIN):
        print(f"❌ Kafka binaries not found at: {KAFKA_BIN}")
        raise KafkaEnvironmentError(f"Kafka binaries missing at {KAFKA_BIN}")
    
    print(f"✓ Kafka binaries found: {KAFKA_BIN}")
    
    # Check for critical binaries
    critical_binaries = [
        "kafka-server-start.sh",
        "kafka-server-stop.sh",
        "zookeeper-server-start.sh",
        "kafka-topics.sh",
        "kafka-console-producer.sh",
        "kafka-console-consumer.sh"
    ]
    
    missing_binaries = []
    for binary in critical_binaries:
        binary_path = os.path.join(KAFKA_BIN, binary)
        if not os.path.exists(binary_path):
            missing_binaries.append(binary)
    
    if missing_binaries:
        print(f"❌ Missing Kafka binaries: {', '.join(missing_binaries)}")
        raise KafkaEnvironmentError("Incomplete Kafka installation")
    
    print(f"✓ All critical binaries present ({len(critical_binaries)} checked)")
    
    # Check config directory
    if not os.path.exists(KAFKA_CONFIG):
        print(f"❌ Kafka config directory not found at: {KAFKA_CONFIG}")
        raise KafkaEnvironmentError(f"Config directory missing at {KAFKA_CONFIG}")
    
    print(f"✓ Kafka config directory found: {KAFKA_CONFIG}")
    
    # Check for configuration files
    if not os.path.exists(ZOOKEEPER_CONFIG):
        print(f"❌ ZooKeeper configuration not found: {ZOOKEEPER_CONFIG}")
        raise KafkaEnvironmentError("ZooKeeper configuration missing")
    
    print(f"✓ ZooKeeper config found: {ZOOKEEPER_CONFIG}")
    
    if not os.path.exists(SERVER_CONFIG):
        print(f"❌ Kafka server configuration not found: {SERVER_CONFIG}")
        raise KafkaEnvironmentError("Kafka server configuration missing")
    
    print(f"✓ Kafka server config found: {SERVER_CONFIG}")
    
    print("\n✅ Kafka installation validated successfully!")
    return True


def is_process_running(process_name):
    """
    Check if a process is running using ps command.
    
    Args:
        process_name (str): Process name to search for
    
    Returns:
        bool: True if process is running, False otherwise
    """
    try:
        result = subprocess.run(
            ["ps", "-ef"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Filter out grep itself and check for the process
        lines = result.stdout.split('\n')
        for line in lines:
            if process_name in line and 'grep' not in line:
                return True
        
        return False
    except Exception as e:
        print(f"⚠ Error checking process status: {e}")
        return False


def check_services_status():
    """
    Check if ZooKeeper and Kafka services are running.
    
    Returns:
        tuple: (zookeeper_running, kafka_running)
    
    Raises:
        KafkaEnvironmentError: If services are not running
    """
    print("\n2️⃣  Checking Service Status...")
    
    # Check ZooKeeper
    zk_running = is_process_running("zookeeper")
    if zk_running:
        print("✓ ZooKeeper is running")
    else:
        print("❌ ZooKeeper is NOT running")
    
    # Check Kafka Broker
    kafka_running = is_process_running("kafka.Kafka")
    if kafka_running:
        print("✓ Kafka Broker is running")
    else:
        print("❌ Kafka Broker is NOT running")
    
    # If either is not running, show instructions
    if not zk_running or not kafka_running:
        print("\n" + "="*60)
        print("⚠️  KAFKA SERVICES NOT RUNNING")
        print("="*60)
        
        if not zk_running:
            print("\n📌 To start ZooKeeper:")
            print(f"   cd {KAFKA_HOME}")
            print(f"   bin/zookeeper-server-start.sh config/zookeeper.properties &")
            print("   (Or run in a separate terminal without '&')")
        
        if not kafka_running:
            print("\n📌 To start Kafka Broker:")
            print(f"   cd {KAFKA_HOME}")
            print(f"   bin/kafka-server-start.sh config/server.properties &")
            print("   (Or run in a separate terminal without '&')")
            print("\n   Note: Start ZooKeeper first, then Kafka Broker")
        
        print("\n" + "="*60)
        raise KafkaEnvironmentError("Required Kafka services are not running")
    
    print("\n✅ All Kafka services are running!")
    return zk_running, kafka_running


def read_server_properties():
    """
    Read and display key configuration from server.properties.
    
    Returns:
        dict: Configuration key-value pairs
    """
    print("\n3️⃣  Reading Kafka Server Configuration...")
    
    config = {}
    important_keys = ['listeners', 'log.dirs', 'broker.id', 'num.partitions', 
                     'log.retention.hours', 'zookeeper.connect']
    
    try:
        with open(SERVER_CONFIG, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in important_keys:
                        config[key] = value
        
        print("\n📋 Key Configuration Values:")
        print("-" * 60)
        for key in important_keys:
            value = config.get(key, 'Not set')
            print(f"   {key:<25} = {value}")
        print("-" * 60)
        
        return config
        
    except Exception as e:
        print(f"⚠ Warning: Could not read server.properties: {e}")
        return {}


def test_broker_connection(broker=DEFAULT_BROKER, timeout=10):
    """
    Test connection to Kafka broker using KafkaAdminClient.
    
    Args:
        broker (str): Broker address (default: localhost:9092)
        timeout (int): Connection timeout in seconds
    
    Returns:
        bool: True if connection successful, False otherwise
    
    Raises:
        KafkaEnvironmentError: If broker is not reachable
    """
    print(f"\n4️⃣  Testing Kafka Broker Connection...")
    print(f"   Connecting to: {broker}")
    
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=broker,
            client_id='kafka_env_validator',
            request_timeout_ms=timeout * 1000
        )
        
        # Try to get cluster metadata
        cluster_metadata = admin_client.list_topics()
        
        print(f"✓ Successfully connected to Kafka broker at {broker}")
        print(f"✓ Cluster has {len(cluster_metadata)} topic(s)")
        
        admin_client.close()
        return True
        
    except NoBrokersAvailable:
        print(f"\n❌ Kafka Broker not reachable at {broker}")
        print(f"\n⚠️  Please ensure Kafka is running and accessible.")
        print(f"   Check that server.properties has correct listener configuration.")
        raise KafkaEnvironmentError(f"Kafka broker not reachable at {broker}")
        
    except KafkaError as e:
        print(f"\n❌ Kafka connection error: {e}")
        raise KafkaEnvironmentError(f"Kafka connection failed: {e}")
        
    except Exception as e:
        print(f"\n❌ Unexpected error connecting to Kafka: {e}")
        raise KafkaEnvironmentError(f"Connection test failed: {e}")


def verify_admin_api():
    """
    Verify Kafka Admin API functionality by creating and deleting a test topic.
    
    Returns:
        bool: True if Admin API is functional, False otherwise
    """
    print("\n5️⃣  Verifying Kafka Admin API...")
    
    test_topic_name = "__connection_check__"
    
    try:
        # Create admin client
        admin_client = KafkaAdminClient(
            bootstrap_servers=DEFAULT_BROKER,
            client_id='admin_api_validator'
        )
        
        # Create test topic
        print(f"   Creating test topic: {test_topic_name}")
        test_topic = NewTopic(
            name=test_topic_name,
            num_partitions=1,
            replication_factor=1
        )
        
        try:
            admin_client.create_topics(new_topics=[test_topic], validate_only=False)
            print(f"✓ Test topic created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"✓ Test topic already exists (will delete)")
            else:
                raise
        
        # Small delay to ensure topic is created
        time.sleep(1)
        
        # Delete test topic
        print(f"   Deleting test topic: {test_topic_name}")
        admin_client.delete_topics(topics=[test_topic_name])
        print(f"✓ Test topic deleted successfully")
        
        admin_client.close()
        
        print("\n✅ Kafka Admin API is fully functional!")
        return True
        
    except Exception as e:
        print(f"\n⚠ Warning: Admin API test failed: {e}")
        print(f"   This may affect dynamic topic creation functionality.")
        return False


def start_kafka_services(background=True):
    """
    Start ZooKeeper and Kafka services programmatically.
    
    Args:
        background (bool): If True, start as background processes
    
    Returns:
        tuple: (zookeeper_process, kafka_process)
    
    Note:
        This function starts services but doesn't wait for them to be ready.
        You may need to add a delay after calling this function.
    """
    print("\n🚀 Starting Kafka Services...")
    
    processes = []
    
    try:
        # Start ZooKeeper
        zk_cmd = [
            os.path.join(KAFKA_BIN, "zookeeper-server-start.sh"),
            ZOOKEEPER_CONFIG
        ]
        
        print("   Starting ZooKeeper...")
        zk_process = subprocess.Popen(
            zk_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=KAFKA_HOME
        )
        processes.append(("ZooKeeper", zk_process))
        print("✓ ZooKeeper started (PID: {})".format(zk_process.pid))
        
        # Wait a bit for ZooKeeper to initialize
        print("   Waiting for ZooKeeper to initialize (5 seconds)...")
        time.sleep(5)
        
        # Start Kafka Broker
        kafka_cmd = [
            os.path.join(KAFKA_BIN, "kafka-server-start.sh"),
            SERVER_CONFIG
        ]
        
        print("   Starting Kafka Broker...")
        kafka_process = subprocess.Popen(
            kafka_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=KAFKA_HOME
        )
        processes.append(("Kafka Broker", kafka_process))
        print("✓ Kafka Broker started (PID: {})".format(kafka_process.pid))
        
        # Wait a bit for Kafka to initialize
        print("   Waiting for Kafka to initialize (10 seconds)...")
        time.sleep(10)
        
        print("\n✅ Kafka services started successfully!")
        print("   Note: Services are running in background")
        print("   To stop: kill -9 {} {}".format(zk_process.pid, kafka_process.pid))
        
        return zk_process, kafka_process
        
    except Exception as e:
        print(f"\n❌ Failed to start Kafka services: {e}")
        # Kill any started processes
        for name, proc in processes:
            try:
                proc.kill()
                print(f"   Killed {name} (PID: {proc.pid})")
            except:
                pass
        raise KafkaEnvironmentError(f"Failed to start services: {e}")


def verify_kafka_connection(broker=DEFAULT_BROKER, auto_start=False, validate_admin=True):
    """
    Complete Kafka environment validation.
    
    This is the main entry point that runs all validation checks:
    1. Check Kafka installation
    2. Check service status
    3. Read server configuration
    4. Test broker connection
    5. Verify Admin API (optional)
    
    Args:
        broker (str): Broker address to test
        auto_start (bool): If True, attempt to start services if not running
        validate_admin (bool): If True, test Admin API functionality
    
    Returns:
        bool: True if all checks pass, False otherwise
    
    Raises:
        KafkaEnvironmentError: If any critical check fails
        SystemExit: Exits with code 1 if validation fails
    """
    try:
        # Step 1: Check installation
        check_kafka_installation()
        
        # Step 2: Check services
        try:
            check_services_status()
        except KafkaEnvironmentError:
            if auto_start:
                print("\n🔧 Attempting to auto-start Kafka services...")
                start_kafka_services()
            else:
                raise
        
        # Step 3: Read configuration
        config = read_server_properties()
        
        # Step 4: Test connection
        test_broker_connection(broker)
        
        # Step 5: Verify Admin API (optional)
        if validate_admin:
            verify_admin_api()
        
        # All checks passed
        print("\n" + "="*60)
        print("✅ ALL KAFKA ENVIRONMENT CHECKS PASSED")
        print("="*60)
        print("🚀 Ready to start Kafka-based applications!\n")
        
        return True
        
    except KafkaEnvironmentError as e:
        print("\n" + "="*60)
        print("❌ KAFKA ENVIRONMENT VALIDATION FAILED")
        print("="*60)
        print(f"Error: {e}")
        print("\nPlease fix the issues above before proceeding.")
        print("="*60 + "\n")
        
        # Exit with error code
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Validation interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def quick_check(broker=DEFAULT_BROKER):
    """
    Quick connection check without full validation.
    Useful for lightweight checks in scripts.
    
    Args:
        broker (str): Broker address to test
    
    Returns:
        bool: True if broker is reachable, False otherwise
    """
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=broker,
            client_id='quick_check',
            request_timeout_ms=5000
        )
        admin_client.list_topics()
        admin_client.close()
        return True
    except:
        return False


if __name__ == '__main__':
    """
    Run validation when executed directly.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka Environment Validator')
    parser.add_argument('--broker', default=DEFAULT_BROKER, 
                       help=f'Kafka broker address (default: {DEFAULT_BROKER})')
    parser.add_argument('--auto-start', action='store_true',
                       help='Automatically start Kafka services if not running')
    parser.add_argument('--skip-admin', action='store_true',
                       help='Skip Admin API validation')
    parser.add_argument('--quick', action='store_true',
                       help='Quick connection check only')
    
    args = parser.parse_args()
    
    if args.quick:
        print("🔍 Quick connection check...")
        if quick_check(args.broker):
            print(f"✅ Kafka broker reachable at {args.broker}")
            sys.exit(0)
        else:
            print(f"❌ Kafka broker NOT reachable at {args.broker}")
            sys.exit(1)
    else:
        verify_kafka_connection(
            broker=args.broker,
            auto_start=args.auto_start,
            validate_admin=not args.skip_admin
        )
