"""
Kafka Broker - Topic Manager Service
Manages topic lifecycle via Kafka Admin API.

This service runs on the Kafka broker system and:
1. Monitors database for approved topics → Creates them in Kafka
2. Monitors database for topics marked for deletion → Deletes them from Kafka
3. Updates topic status in database (pending → approved → active → inactive/deleted)

This should run alongside the Kafka broker process.
"""

import sys
import os
import time
import json
import argparse
from threading import Thread, Event
from datetime import datetime

from kafka.admin import KafkaAdminClient, NewTopic, ConfigResource, ConfigResourceType
from kafka.errors import TopicAlreadyExistsError, UnknownTopicOrPartitionError, KafkaError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import get_topics_by_status, update_topic_status, get_connection

class BrokerTopicManager:
    """
    Broker-side service that manages Kafka topics via Admin API
    """
    
    def __init__(self, config, stop_event=None):
        """
        Initialize the Broker Topic Manager.
        
        Args:
            config (dict): Configuration dictionary with Kafka settings
            stop_event (Event): Threading event to signal shutdown (optional)
        """
        self.config = config
        self.stop_event = stop_event or Event()
        self.admin_client = None
        self.poll_interval = config.get('topic_manager_poll_interval', 5)
        self.broker_id = config.get('broker_id', 0)
        
        print(f"🔧 Broker Topic Manager initialized (Broker ID: {self.broker_id})")
        
    def connect_admin_client(self):
        """Connect to Kafka Admin Client"""
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.config['bootstrap_servers'],
                client_id=f'broker_topic_manager_{self.broker_id}'
            )
            print(f"✓ Topic Manager: Connected to Kafka Admin API at {self.config['bootstrap_servers']}")
            return True
        except Exception as e:
            print(f"✗ Topic Manager: Failed to connect to Kafka Admin API: {e}")
            return False
    
    def create_kafka_topic(self, topic_name):
        """
        Create a topic in Kafka.
        
        Args:
            topic_name (str): Name of the topic to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create topic with specified configuration
            topic = NewTopic(
                name=topic_name,
                num_partitions=self.config.get('default_partitions', 3),
                replication_factor=self.config.get('default_replication_factor', 1)
            )
            
            self.admin_client.create_topics(new_topics=[topic], validate_only=False)
            print(f"✓ Topic Manager: Created Kafka topic '{topic_name}'")
            print(f"  ├─ Partitions: {self.config.get('default_partitions', 3)}")
            print(f"  └─ Replication Factor: {self.config.get('default_replication_factor', 1)}")
            return True
            
        except TopicAlreadyExistsError:
            print(f"⚠ Topic Manager: Topic '{topic_name}' already exists in Kafka")
            return True  # Consider it success since topic exists
            
        except KafkaError as e:
            print(f"✗ Topic Manager: Kafka error creating topic '{topic_name}': {e}")
            return False
            
        except Exception as e:
            print(f"✗ Topic Manager: Unexpected error creating topic '{topic_name}': {e}")
            return False
    
    def delete_kafka_topic(self, topic_name):
        """
        Delete a topic from Kafka.
        
        Args:
            topic_name (str): Name of the topic to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.admin_client.delete_topics(topics=[topic_name])
            print(f"✓ Topic Manager: Deleted Kafka topic '{topic_name}'")
            return True
            
        except UnknownTopicOrPartitionError:
            print(f"⚠ Topic Manager: Topic '{topic_name}' does not exist in Kafka")
            return True  # Consider it success since topic is gone
            
        except KafkaError as e:
            print(f"✗ Topic Manager: Kafka error deleting topic '{topic_name}': {e}")
            return False
            
        except Exception as e:
            print(f"✗ Topic Manager: Unexpected error deleting topic '{topic_name}': {e}")
            return False
    
    def get_kafka_topics(self):
        """
        Get list of all topics in Kafka cluster.
        
        Returns:
            set: Set of topic names, or empty set on error
        """
        try:
            topics = self.admin_client.list_topics()
            return set(topics)
        except Exception as e:
            print(f"✗ Topic Manager: Error listing topics: {e}")
            return set()
    
    def process_approved_topics(self):
        """
        Process approved topics: Create them in Kafka and mark as active
        """
        try:
            approved_topics = get_topics_by_status('approved')
            
            if approved_topics:
                print(f"📋 Topic Manager: Found {len(approved_topics)} approved topic(s) to create")
                
                for topic in approved_topics:
                    topic_name = topic['name']
                    print(f"🔨 Topic Manager: Creating '{topic_name}'...")
                    
                    # Create topic in Kafka
                    if self.create_kafka_topic(topic_name):
                        # Update status to 'active' in database
                        if update_topic_status(topic_name, 'active'):
                            print(f"✅ Topic Manager: '{topic_name}' is now ACTIVE")
                        else:
                            print(f"✗ Topic Manager: Failed to update status for '{topic_name}'")
                    else:
                        print(f"✗ Topic Manager: Failed to create '{topic_name}' in Kafka")
                        
        except Exception as e:
            print(f"✗ Topic Manager: Error processing approved topics: {e}")
    
    def process_inactive_topics(self):
        """
        Process inactive topics: Delete them from Kafka and mark as deleted
        """
        try:
            inactive_topics = get_topics_by_status('inactive')
            
            if inactive_topics:
                print(f"🗑️  Topic Manager: Found {len(inactive_topics)} inactive topic(s) to delete")
                
                for topic in inactive_topics:
                    topic_name = topic['name']
                    print(f"🔨 Topic Manager: Deleting '{topic_name}'...")
                    
                    # Delete topic from Kafka
                    if self.delete_kafka_topic(topic_name):
                        # Update status to 'deleted' in database
                        if update_topic_status(topic_name, 'deleted'):
                            print(f"✅ Topic Manager: '{topic_name}' is now DELETED")
                        else:
                            print(f"✗ Topic Manager: Failed to update status for '{topic_name}'")
                    else:
                        print(f"✗ Topic Manager: Failed to delete '{topic_name}' from Kafka")
                        
        except Exception as e:
            print(f"✗ Topic Manager: Error processing inactive topics: {e}")
    
    def sync_orphaned_topics(self):
        """
        Sync orphaned topics: Find topics in Kafka but not in DB (optional cleanup)
        """
        try:
            kafka_topics = self.get_kafka_topics()
            
            # Filter out internal Kafka topics
            kafka_topics = {t for t in kafka_topics if not t.startswith('_')}
            
            if not kafka_topics:
                return
            
            # Get all active topics from database
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM topics WHERE status = 'active'")
            db_topics = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            # Find orphaned topics (in Kafka but not in DB as active)
            orphaned = kafka_topics - db_topics
            
            if orphaned:
                print(f"⚠️  Topic Manager: Found {len(orphaned)} orphaned topic(s) in Kafka:")
                for topic in orphaned:
                    print(f"   - {topic}")
                print("   (These topics exist in Kafka but are not marked as 'active' in DB)")
                
        except Exception as e:
            print(f"✗ Topic Manager: Error syncing orphaned topics: {e}")
    
    def run_once(self):
        """Execute one cycle of topic management"""
        print(f"\n{'='*70}")
        print(f"🔄 Topic Manager: Running cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Process approved topics (create)
        self.process_approved_topics()
        
        # Process inactive topics (delete)
        self.process_inactive_topics()
        
        # Optional: Check for orphaned topics
        if self.config.get('sync_orphaned_topics', False):
            self.sync_orphaned_topics()
    
    def run_loop(self):
        """Main loop to continuously manage topics"""
        while not self.stop_event.is_set():
            try:
                self.run_once()
                
                # Wait before next poll
                print(f"\n⏸️  Waiting {self.poll_interval}s until next check...")
                self.stop_event.wait(self.poll_interval)
                
            except Exception as e:
                print(f"✗ Topic Manager: Error in main loop: {e}")
                self.stop_event.wait(self.poll_interval)
    
    def start(self):
        """Start the topic manager service"""
        print("\n" + "="*70)
        print("🚀 KAFKA BROKER - TOPIC MANAGER SERVICE")
        print("="*70)
        print(f"Bootstrap Servers: {self.config['bootstrap_servers']}")
        print(f"Poll Interval: {self.poll_interval}s")
        print(f"Broker ID: {self.broker_id}")
        print("="*70 + "\n")
        
        # Connect to Kafka Admin API
        if not self.connect_admin_client():
            print("✗ Topic Manager: Cannot start without Kafka connection")
            print("⚠️  Make sure Kafka broker is running!")
            return False
        
        print(f"👀 Topic Manager: Monitoring database for topic lifecycle events...")
        print(f"   - 'approved' → Create in Kafka → 'active'")
        print(f"   - 'inactive' → Delete from Kafka → 'deleted'")
        print("")
        
        try:
            self.run_loop()
        except KeyboardInterrupt:
            print("\n⏹️  Stopping Topic Manager...")
        finally:
            if self.admin_client:
                self.admin_client.close()
            print("🛑 Topic Manager: Stopped")
        
        return True
    
    def cleanup(self):
        """Cleanup resources"""
        if self.admin_client:
            self.admin_client.close()

def load_config(config_path=None):
    """Load configuration from JSON file"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✓ Loaded configuration from: {config_path}")
        return config
    except FileNotFoundError:
        print(f"✗ Configuration file not found: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in configuration file: {e}")
        return None

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Kafka Broker Topic Manager Service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default config.json
  python3 broker/topic_manager.py
  
  # Use custom config file
  python3 broker/topic_manager.py --config /path/to/config.json
  
  # Run once and exit (no loop)
  python3 broker/topic_manager.py --once
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration JSON file (default: config.json)'
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (do not loop)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    if not config:
        print("✗ Failed to load configuration. Exiting.")
        return 1
    
    # Initialize database
    from admin.db_setup import initialize_database
    initialize_database()
    
    # Create topic manager
    stop_event = Event()
    manager = BrokerTopicManager(config, stop_event)
    
    try:
        if args.once:
            # Run once and exit
            if manager.connect_admin_client():
                manager.run_once()
                manager.cleanup()
            return 0
        else:
            # Run continuous loop
            manager.start()
            return 0
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        stop_event.set()
        manager.cleanup()
        return 0
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
