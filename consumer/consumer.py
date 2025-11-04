"""
Dynamic Kafka Consumer
Dynamically subscribes to active topics and consumes messages in real-time.

Features:
- Queries database for active topics
- Allows users to subscribe/unsubscribe from topics
- Consumes messages from subscribed topics
- Multi-consumer support with user IDs

Usage:
    python3 consumer.py [user_id]
    
    Default user_id is 1 if not specified.

Commands (interactive mode):
    list        - List all active topics
    subscribed  - Show topics you're subscribed to
    subscribe <topic1> <topic2> ...   - Subscribe to topics
    unsubscribe <topic1> <topic2> ... - Unsubscribe from topics
    refresh     - Refresh subscription from database
    help        - Show help
    quit        - Exit consumer
"""

import sys
import os
import json
import time
from threading import Thread, Event

from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import (
    get_topics_by_status,
    subscribe_user_to_topic,
    unsubscribe_user_from_topic,
    get_user_subscriptions,
    initialize_database
)
from kafka_env_setup import verify_kafka_connection

class DynamicConsumer:
    """
    Dynamic Kafka Consumer that subscribes to topics based on user preferences
    """
    
    def __init__(self, config, user_id=1):
        """
        Initialize the consumer.
        
        Args:
            config (dict): Configuration dictionary
            user_id (int): User identifier
        """
        self.config = config
        self.user_id = user_id
        self.consumer = None
        self.stop_event = Event()
        self.consumer_thread = None
        self.subscribed_topics = []
        
        # Initialize database
        initialize_database()
    
    def connect_consumer(self):
        """Connect to Kafka Consumer"""
        try:
            self.consumer = KafkaConsumer(
                bootstrap_servers=self.config['bootstrap_servers'],
                group_id=f"consumer_group_{self.user_id}",
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset=self.config.get('auto_offset_reset', 'latest'),
                enable_auto_commit=True,
                consumer_timeout_ms=1000  # Timeout to allow checking stop_event
            )
            print(f"✓ Consumer: Connected to Kafka (User ID: {self.user_id})")
            return True
        except Exception as e:
            print(f"✗ Consumer: Failed to connect to Kafka: {e}")
            return False
    
    def get_active_topics(self):
        """
        Get all active topics from database.
        
        Returns:
            list: List of active topic names
        """
        active_topics = get_topics_by_status('active')
        return [t['name'] for t in active_topics]
    
    def load_user_subscriptions(self):
        """Load user subscriptions from database"""
        self.subscribed_topics = get_user_subscriptions(self.user_id)
        return self.subscribed_topics
    
    def subscribe_to_topics(self, topics):
        """
        Subscribe to topics.
        
        Args:
            topics (list): List of topic names to subscribe to
            
        Returns:
            int: Number of successfully subscribed topics
        """
        if not topics:
            print("❌ No topics provided")
            return 0
        
        # Get active topics
        active_topics = self.get_active_topics()
        
        success_count = 0
        for topic in topics:
            topic = topic.strip()
            
            # Check if topic is active
            if topic not in active_topics:
                print(f"⚠ Topic '{topic}' is not active")
                continue
            
            # Add to database
            if subscribe_user_to_topic(self.user_id, topic):
                print(f"✓ Subscribed to '{topic}'")
                success_count += 1
            else:
                print(f"⚠ Already subscribed to '{topic}'")
        
        # Reload subscriptions
        self.load_user_subscriptions()
        
        # Update Kafka consumer subscription
        if self.consumer and self.subscribed_topics:
            self.consumer.subscribe(self.subscribed_topics)
            print(f"📋 Active subscriptions: {', '.join(self.subscribed_topics)}")
        
        return success_count
    
    def unsubscribe_from_topics(self, topics):
        """
        Unsubscribe from topics.
        
        Args:
            topics (list): List of topic names to unsubscribe from
            
        Returns:
            int: Number of successfully unsubscribed topics
        """
        if not topics:
            print("❌ No topics provided")
            return 0
        
        success_count = 0
        for topic in topics:
            topic = topic.strip()
            
            if unsubscribe_user_from_topic(self.user_id, topic):
                print(f"✓ Unsubscribed from '{topic}'")
                success_count += 1
            else:
                print(f"⚠ Not subscribed to '{topic}'")
        
        # Reload subscriptions
        self.load_user_subscriptions()
        
        # Update Kafka consumer subscription
        if self.consumer:
            if self.subscribed_topics:
                self.consumer.subscribe(self.subscribed_topics)
                print(f"📋 Active subscriptions: {', '.join(self.subscribed_topics)}")
            else:
                self.consumer.unsubscribe()
                print("📋 No active subscriptions")
        
        return success_count
    
    def consume_messages(self):
        """Consume messages from subscribed topics (runs in separate thread)"""
        print("📥 Consumer: Listening for messages...")
        
        while not self.stop_event.is_set():
            try:
                # Poll for messages
                for message in self.consumer:
                    if self.stop_event.is_set():
                        break
                    
                    # Display received message
                    print(f"\n📨 [{message.topic}] Message received:")
                    print(f"   Content: {message.value.get('content', 'N/A')}")
                    print(f"   Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.value.get('timestamp', 0)))}")
                    print(f"   Partition: {message.partition} | Offset: {message.offset}")
                    print("> ", end='', flush=True)
                
            except Exception as e:
                if not self.stop_event.is_set():
                    # Only print error if we're not stopping
                    if "timeout" not in str(e).lower():
                        print(f"✗ Consumer: Error consuming messages: {e}")
                time.sleep(1)
        
        print("🛑 Consumer: Stopped listening")
    
    def display_menu(self):
        """Display the consumer menu"""
        print("\n" + "="*60)
        print(f"         KAFKA CONSUMER - User {self.user_id}")
        print("="*60)
        print("Commands:")
        print("  list                           - List all active topics")
        print("  subscribed                     - Show your subscribed topics")
        print("  subscribe <topic1> <topic2>... - Subscribe to topics")
        print("  unsubscribe <topic1> ...       - Unsubscribe from topics")
        print("  refresh                        - Refresh subscriptions")
        print("  help                           - Show this menu")
        print("  quit                           - Exit consumer")
        print("="*60)
    
    def handle_command(self, command):
        """
        Handle user command.
        
        Args:
            command (str): User command string
        """
        command = command.strip()
        
        if not command:
            return True
        
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == 'list':
            active_topics = self.get_active_topics()
            if active_topics:
                print("\n🟢 Active Topics:")
                for i, topic in enumerate(active_topics, 1):
                    subscribed = "✓" if topic in self.subscribed_topics else " "
                    print(f"  [{subscribed}] {i}. {topic}")
            else:
                print("📋 No active topics found")
        
        elif cmd == 'subscribed':
            if self.subscribed_topics:
                print(f"\n📋 You are subscribed to {len(self.subscribed_topics)} topic(s):")
                for i, topic in enumerate(self.subscribed_topics, 1):
                    print(f"  {i}. {topic}")
            else:
                print("📋 You are not subscribed to any topics")
        
        elif cmd == 'subscribe':
            if not args:
                print("❌ Usage: subscribe <topic1> <topic2> ...")
            else:
                self.subscribe_to_topics(args)
        
        elif cmd == 'unsubscribe':
            if not args:
                print("❌ Usage: unsubscribe <topic1> <topic2> ...")
            else:
                self.unsubscribe_from_topics(args)
        
        elif cmd == 'refresh':
            self.load_user_subscriptions()
            if self.consumer and self.subscribed_topics:
                self.consumer.subscribe(self.subscribed_topics)
            print(f"✓ Refreshed subscriptions: {', '.join(self.subscribed_topics) if self.subscribed_topics else 'none'}")
        
        elif cmd == 'help':
            self.display_menu()
        
        elif cmd == 'quit' or cmd == 'exit':
            return False
        
        else:
            print(f"❌ Unknown command: {cmd}")
            print("   Type 'help' for available commands")
        
        return True
    
    def start(self):
        """Start the consumer"""
        print("\n" + "="*60)
        print("  KAFKA DYNAMIC STREAM - CONSUMER")
        print("="*60)
        print(f"User ID: {self.user_id}")
        print(f"Kafka Broker: {self.config['bootstrap_servers']}")
        print("="*60 + "\n")
        
        # Connect to Kafka
        if not self.connect_consumer():
            print("✗ Cannot start consumer without Kafka connection")
            return
        
        # Load existing subscriptions
        self.load_user_subscriptions()
        
        if self.subscribed_topics:
            print(f"📋 Existing subscriptions: {', '.join(self.subscribed_topics)}")
            self.consumer.subscribe(self.subscribed_topics)
        else:
            print("📋 No existing subscriptions")
        
        # Start consumer thread
        self.consumer_thread = Thread(target=self.consume_messages, daemon=True)
        self.consumer_thread.start()
        
        # Display menu
        self.display_menu()
        
        # Interactive command loop
        try:
            while True:
                print("\n> ", end='', flush=True)
                command = input()
                
                if not self.handle_command(command):
                    break
                    
        except EOFError:
            print("\n⏹ EOF detected, stopping...")
        except KeyboardInterrupt:
            print("\n⏹ Interrupted, stopping...")
        
        self.stop()
    
    def stop(self):
        """Stop the consumer"""
        print("\n🛑 Shutting down consumer...")
        
        self.stop_event.set()
        
        # Wait for consumer thread
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=5)
        
        # Close consumer
        if self.consumer:
            self.consumer.close()
        
        print("✓ Consumer stopped")
        print("👋 Goodbye!\n")

def main():
    """Main entry point"""
    # Get user ID from command line argument
    user_id = 1
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except ValueError:
            print(f"⚠ Invalid user_id, using default: 1")
    
    # Load configuration
    try:
        # Validate Kafka environment before starting
        print("🔍 Validating Kafka environment...")
        verify_kafka_connection(validate_admin=False)
        
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create and start consumer
        consumer = DynamicConsumer(config, user_id)
        consumer.start()
        
    except FileNotFoundError as e:
        print(f"✗ Configuration file not found: {e}")
        print("  Make sure 'config.json' exists in the project root")
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in configuration file: {e}")
    except Exception as e:
        print(f"✗ Error starting consumer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
