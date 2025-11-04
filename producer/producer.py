"""
Multi-threaded Producer
Coordinates three threads to manage dynamic topic creation and message publishing.

Threads:
1. Publisher Thread - Publishes messages from queue to Kafka
2. Input Listener Thread - Receives user commands and messages
3. Topic Watcher Thread - Monitors approved topics and creates them in Kafka

Usage:
    python3 producer.py

Commands (in Input Listener):
    create <topic_name>        - Create new topic (pending approval)
    send <topic_name> <msg>    - Send message to active topic
    list                       - List all topics
    active                     - List active topics
    help                       - Show help
    quit                       - Exit
"""

import sys
import os
import json
import time
from threading import Thread, Event
from queue import Queue, Empty

from kafka import KafkaProducer
from kafka.errors import KafkaError

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from admin.db_setup import initialize_database
from kafka_env_setup import verify_kafka_connection

# Import local modules
import topic_watcher as topic_watcher_module
import input_listener as input_listener_module
TopicWatcher = topic_watcher_module.TopicWatcher
InputListener = input_listener_module.InputListener

class Publisher(Thread):
    """
    Thread that publishes messages from queue to Kafka topics
    """
    
    def __init__(self, config, message_queue, stop_event):
        """
        Initialize the Publisher.
        
        Args:
            config (dict): Configuration dictionary
            message_queue (Queue): Queue to receive messages from
            stop_event (Event): Threading event to signal shutdown
        """
        super().__init__(daemon=True)
        self.config = config
        self.message_queue = message_queue
        self.stop_event = stop_event
        self.producer = None
    
    def connect_producer(self):
        """Connect to Kafka Producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config['bootstrap_servers'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks=self.config.get('acks', 1),
                compression_type=self.config.get('compression_type', 'gzip'),
                retries=self.config.get('retries', 3)
            )
            print("✓ Publisher: Connected to Kafka")
            return True
        except Exception as e:
            print(f"✗ Publisher: Failed to connect to Kafka: {e}")
            return False
    
    def publish_message(self, topic, message):
        """
        Publish a message to a Kafka topic.
        
        Args:
            topic (str): Topic name
            message (str): Message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare message data
            message_data = {
                'content': message,
                'timestamp': time.time(),
                'source': 'producer'
            }
            
            # Send to Kafka
            future = self.producer.send(topic, value=message_data, key=topic)
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            print(f"✓ Publisher: Sent to '{topic}' [partition {record_metadata.partition}, offset {record_metadata.offset}]")
            return True
            
        except KafkaError as e:
            print(f"✗ Publisher: Kafka error sending to '{topic}': {e}")
            return False
        except Exception as e:
            print(f"✗ Publisher: Unexpected error sending to '{topic}': {e}")
            return False
    
    def run(self):
        """Run the publisher thread"""
        print("🚀 Publisher: Starting...")
        
        # Connect to Kafka
        if not self.connect_producer():
            print("✗ Publisher: Cannot start without Kafka connection")
            return
        
        print("📤 Publisher: Ready to publish messages...")
        
        while not self.stop_event.is_set():
            try:
                # Get message from queue (with timeout to check stop_event)
                try:
                    message_data = self.message_queue.get(timeout=1)
                except Empty:
                    continue
                
                # Publish message
                topic = message_data.get('topic')
                message = message_data.get('message')
                
                if topic and message:
                    self.publish_message(topic, message)
                else:
                    print("✗ Publisher: Invalid message data")
                
                # Mark task as done
                self.message_queue.task_done()
                
            except Exception as e:
                print(f"✗ Publisher: Error in main loop: {e}")
        
        # Cleanup
        if self.producer:
            self.producer.flush()
            self.producer.close()
        
        print("🛑 Publisher: Stopped")

class ProducerCoordinator:
    """
    Coordinates all producer threads
    """
    
    def __init__(self, config_path='config.json'):
        """
        Initialize the producer coordinator.
        
        Args:
            config_path (str): Path to configuration file
        """
        # Load configuration
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), config_path)
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize database
        initialize_database()
        
        # Create shared resources
        self.message_queue = Queue()
        self.stop_event = Event()
        
        # Create threads
        self.publisher = Publisher(self.config, self.message_queue, self.stop_event)
        self.topic_watcher = TopicWatcher(self.config, self.stop_event)
        self.input_listener = InputListener(self.message_queue, self.stop_event)
    
    def start(self):
        """Start all producer threads"""
        print("\n" + "="*60)
        print("  KAFKA DYNAMIC STREAM - MULTI-THREADED PRODUCER")
        print("="*60)
        print(f"Kafka Broker: {self.config['bootstrap_servers']}")
        print("="*60 + "\n")
        
        # Start threads
        self.publisher.start()
        time.sleep(0.5)  # Small delay between starts
        
        self.topic_watcher.start()
        time.sleep(0.5)
        
        self.input_listener.start()
        
        print("\n✓ All threads started successfully!")
        print("\nType 'help' for available commands\n")
        
        try:
            # Wait for input listener to finish (user quit)
            self.input_listener.join()
        except KeyboardInterrupt:
            print("\n⏹ Keyboard interrupt received...")
            self.stop_event.set()
        
        # Stop all threads
        self.stop()
    
    def stop(self):
        """Stop all producer threads"""
        print("\n🛑 Shutting down producer threads...")
        
        self.stop_event.set()
        
        # Wait for threads to finish
        threads = [self.publisher, self.topic_watcher, self.input_listener]
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        print("✓ All threads stopped")
        print("👋 Producer shutdown complete!\n")

def main():
    """Main entry point"""
    try:
        # Validate Kafka environment before starting
        print("🔍 Validating Kafka environment...")
        verify_kafka_connection(validate_admin=True)
        
        coordinator = ProducerCoordinator()
        coordinator.start()
    except FileNotFoundError as e:
        print(f"✗ Configuration file not found: {e}")
        print("  Make sure 'config.json' exists in the project root")
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in configuration file: {e}")
    except Exception as e:
        print(f"✗ Error starting producer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
