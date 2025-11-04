"""
Input Listener Module
Receives user input for creating new topics and adding messages to publish.

This module runs as a separate thread that:
1. Accepts user commands to create new topics
2. Accepts messages to be published to existing topics
3. Adds topics to database as 'pending'
4. Enqueues messages for the publisher thread
"""

import sys
import os
import json
from threading import Thread, Event
from queue import Queue

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import add_topic, get_topics_by_status, get_all_topics

class InputListener(Thread):
    """
    Thread that listens for user input to create topics and publish messages
    """
    
    def __init__(self, message_queue, stop_event):
        """
        Initialize the Input Listener.
        
        Args:
            message_queue (Queue): Queue to put messages for publishing
            stop_event (Event): Threading event to signal shutdown
        """
        super().__init__(daemon=True)
        self.message_queue = message_queue
        self.stop_event = stop_event
    
    def display_menu(self):
        """Display the input menu"""
        print("\n" + "="*60)
        print("         PRODUCER INPUT LISTENER")
        print("="*60)
        print("Commands:")
        print("  1. create <topic_name>        - Create a new topic")
        print("  2. send <topic_name> <message> - Send message to topic")
        print("  3. list                        - List all topics")
        print("  4. active                      - List active topics")
        print("  5. help                        - Show this menu")
        print("  6. quit                        - Exit")
        print("="*60)
    
    def handle_create_topic(self, args):
        """
        Handle topic creation command.
        
        Args:
            args (list): Command arguments
        """
        if len(args) < 1:
            print("❌ Usage: create <topic_name>")
            return
        
        topic_name = args[0].strip()
        
        if not topic_name:
            print("❌ Topic name cannot be empty")
            return
        
        # Validate topic name (Kafka naming conventions)
        if not all(c.isalnum() or c in ['_', '-', '.'] for c in topic_name):
            print("❌ Topic name can only contain alphanumeric characters, underscores, hyphens, and dots")
            return
        
        # Add topic to database as 'pending'
        if add_topic(topic_name, 'pending'):
            print(f"✓ Topic '{topic_name}' created with status: PENDING")
            print("  → Waiting for admin approval...")
        else:
            print(f"✗ Failed to create topic '{topic_name}' (may already exist)")
    
    def handle_send_message(self, args):
        """
        Handle message sending command.
        
        Args:
            args (list): Command arguments
        """
        if len(args) < 2:
            print("❌ Usage: send <topic_name> <message>")
            return
        
        topic_name = args[0].strip()
        message = ' '.join(args[1:]).strip()
        
        if not topic_name or not message:
            print("❌ Topic name and message cannot be empty")
            return
        
        # Check if topic is active
        active_topics = get_topics_by_status('active')
        active_topic_names = [t['name'] for t in active_topics]
        
        if topic_name not in active_topic_names:
            print(f"❌ Topic '{topic_name}' is not active. Available active topics:")
            if active_topic_names:
                for name in active_topic_names:
                    print(f"   - {name}")
            else:
                print("   (none)")
            return
        
        # Enqueue message for publisher
        message_data = {
            'topic': topic_name,
            'message': message
        }
        self.message_queue.put(message_data)
        print(f"✓ Message queued for topic '{topic_name}'")
    
    def handle_list_topics(self):
        """List all topics with their statuses"""
        topics = get_all_topics()
        
        if not topics:
            print("📋 No topics found in the database")
            return
        
        print("\n📋 All Topics:")
        print(f"{'Name':<30} {'Status':<12}")
        print("-" * 45)
        for topic in topics:
            status_icon = {
                'pending': '⏳',
                'approved': '✓',
                'active': '🟢'
            }.get(topic['status'], '•')
            print(f"{topic['name']:<30} {status_icon} {topic['status']:<10}")
    
    def handle_list_active_topics(self):
        """List only active topics"""
        active_topics = get_topics_by_status('active')
        
        if not active_topics:
            print("📋 No active topics found")
            return
        
        print("\n🟢 Active Topics:")
        for i, topic in enumerate(active_topics, 1):
            print(f"  {i}. {topic['name']}")
    
    def process_command(self, command):
        """
        Process a user command.
        
        Args:
            command (str): User command string
        """
        command = command.strip()
        
        if not command:
            return
        
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        if cmd == 'create':
            self.handle_create_topic(args)
        
        elif cmd == 'send':
            self.handle_send_message(args)
        
        elif cmd == 'list':
            self.handle_list_topics()
        
        elif cmd == 'active':
            self.handle_list_active_topics()
        
        elif cmd == 'help':
            self.display_menu()
        
        elif cmd == 'quit' or cmd == 'exit':
            print("\n👋 Exiting Input Listener...")
            self.stop_event.set()
        
        else:
            print(f"❌ Unknown command: {cmd}")
            print("   Type 'help' for available commands")
    
    def run(self):
        """Run the input listener thread"""
        print("🚀 Input Listener: Starting...")
        self.display_menu()
        
        while not self.stop_event.is_set():
            try:
                print("\n> ", end='', flush=True)
                command = input()
                
                if command:
                    self.process_command(command)
                    
            except EOFError:
                print("\n⏹ EOF detected, stopping...")
                self.stop_event.set()
                break
            except KeyboardInterrupt:
                print("\n⏹ Interrupted, stopping...")
                self.stop_event.set()
                break
            except Exception as e:
                print(f"✗ Input Listener: Error processing command: {e}")
        
        print("🛑 Input Listener: Stopped")

def test_input_listener():
    """Test function for input listener"""
    from queue import Queue
    
    # Create message queue and stop event
    message_queue = Queue()
    stop_event = Event()
    
    # Create and start listener
    listener = InputListener(message_queue, stop_event)
    listener.start()
    
    # Wait for completion
    listener.join()

if __name__ == '__main__':
    test_input_listener()
