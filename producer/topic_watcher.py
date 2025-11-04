"""
Topic Watcher Module
Monitors the database for approved topics and creates them in Kafka using Admin API.

This module runs as a separate thread that:
1. Polls the database for topics with status 'approved'
2. Creates them in Kafka using KafkaAdminClient
3. Updates their status to 'active' in the database
"""

import sys
import os
import time
import json
from threading import Thread, Event

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import get_topics_by_status, update_topic_status

class TopicWatcher(Thread):
    """
    Thread that watches for approved topics and creates them in Kafka
    """
    
    def __init__(self, config, stop_event):
        """
        Initialize the Topic Watcher.
        
        Args:
            config (dict): Configuration dictionary with Kafka settings
            stop_event (Event): Threading event to signal shutdown
        """
        super().__init__(daemon=True)
        self.config = config
        self.stop_event = stop_event
        self.admin_client = None
        self.poll_interval = config.get('topic_watcher_poll_interval', 5)
        
    def connect_admin_client(self):
        """Connect to Kafka Admin Client"""
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.config['bootstrap_servers'],
                client_id='topic_watcher_admin'
            )
            print("✓ Topic Watcher: Connected to Kafka Admin API")
            return True
        except Exception as e:
            print(f"✗ Topic Watcher: Failed to connect to Kafka Admin API: {e}")
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
            print(f"✓ Topic Watcher: Created Kafka topic '{topic_name}'")
            return True
            
        except TopicAlreadyExistsError:
            print(f"⚠ Topic Watcher: Topic '{topic_name}' already exists in Kafka")
            return True  # Consider it success since topic exists
            
        except KafkaError as e:
            print(f"✗ Topic Watcher: Kafka error creating topic '{topic_name}': {e}")
            return False
            
        except Exception as e:
            print(f"✗ Topic Watcher: Unexpected error creating topic '{topic_name}': {e}")
            return False
    
    def watch_and_create_topics(self):
        """
        Main loop to watch for approved topics and create them in Kafka
        """
        while not self.stop_event.is_set():
            try:
                # Get all approved topics from database
                approved_topics = get_topics_by_status('approved')
                
                if approved_topics:
                    print(f"📋 Topic Watcher: Found {len(approved_topics)} approved topic(s)")
                    
                    for topic in approved_topics:
                        topic_name = topic['name']
                        print(f"🔨 Topic Watcher: Processing '{topic_name}'...")
                        
                        # Create topic in Kafka
                        if self.create_kafka_topic(topic_name):
                            # Update status to 'active' in database
                            if update_topic_status(topic_name, 'active'):
                                print(f"✓ Topic Watcher: '{topic_name}' is now ACTIVE")
                            else:
                                print(f"✗ Topic Watcher: Failed to update status for '{topic_name}'")
                        else:
                            print(f"✗ Topic Watcher: Failed to create '{topic_name}' in Kafka")
                
                # Wait before next poll
                self.stop_event.wait(self.poll_interval)
                
            except Exception as e:
                print(f"✗ Topic Watcher: Error in main loop: {e}")
                self.stop_event.wait(self.poll_interval)
    
    def run(self):
        """Run the topic watcher thread"""
        print("🚀 Topic Watcher: Starting...")
        
        # Connect to Kafka Admin API
        if not self.connect_admin_client():
            print("✗ Topic Watcher: Cannot start without Kafka connection")
            return
        
        print(f"👀 Topic Watcher: Monitoring for approved topics (polling every {self.poll_interval}s)...")
        
        try:
            self.watch_and_create_topics()
        finally:
            if self.admin_client:
                self.admin_client.close()
            print("🛑 Topic Watcher: Stopped")

def test_topic_watcher():
    """Test function for topic watcher"""
    import json
    from kafka_env_setup import verify_kafka_connection
    
    # Validate Kafka environment first
    print("🔍 Validating Kafka environment...")
    verify_kafka_connection(validate_admin=True)
    
    # Load config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create stop event
    stop_event = Event()
    
    # Create and start watcher
    watcher = TopicWatcher(config, stop_event)
    watcher.start()
    
    try:
        # Let it run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹ Stopping Topic Watcher...")
        stop_event.set()
        watcher.join(timeout=5)
        print("✓ Topic Watcher stopped")

if __name__ == '__main__':
    test_topic_watcher()
