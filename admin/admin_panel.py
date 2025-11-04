"""
Admin Panel Module
Interactive CLI for managing topic approvals and viewing system status.

Features:
- View all pending topics
- Approve or reject topics
- View all topics with their statuses
- View user subscriptions
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import db_setup
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import (
    get_topics_by_status,
    get_all_topics,
    update_topic_status,
    get_all_subscriptions,
    initialize_database
)

class AdminPanel:
    """Admin Panel for managing topics and viewing system status"""
    
    def __init__(self):
        """Initialize the admin panel"""
        initialize_database()
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("         KAFKA DYNAMIC STREAM - ADMIN PANEL")
        print("="*60)
        print("1. View Pending Topics")
        print("2. Approve Topics")
        print("3. Reject Topics")
        print("4. View All Topics")
        print("5. View User Subscriptions")
        print("6. Exit")
        print("="*60)
    
    def view_pending_topics(self):
        """Display all pending topics"""
        print("\n--- Pending Topics ---")
        pending = get_topics_by_status('pending')
        
        if not pending:
            print("No pending topics found.")
            return
        
        print(f"{'ID':<5} {'Topic Name':<30} {'Created At':<20}")
        print("-" * 60)
        for topic in pending:
            print(f"{topic['id']:<5} {topic['name']:<30} {topic['created_at']:<20}")
    
    def approve_topics(self):
        """Approve pending topics"""
        self.view_pending_topics()
        pending = get_topics_by_status('pending')
        
        if not pending:
            return
        
        print("\nEnter topic names to approve (comma-separated) or 'all' for all:")
        choice = input(">> ").strip()
        
        if choice.lower() == 'all':
            topics_to_approve = [t['name'] for t in pending]
        else:
            topics_to_approve = [name.strip() for name in choice.split(',')]
        
        approved_count = 0
        for topic_name in topics_to_approve:
            if update_topic_status(topic_name, 'approved'):
                print(f"✓ Approved: {topic_name}")
                approved_count += 1
            else:
                print(f"✗ Failed to approve: {topic_name}")
        
        print(f"\nTotal approved: {approved_count}/{len(topics_to_approve)}")
    
    def reject_topics(self):
        """Reject (delete) pending topics"""
        self.view_pending_topics()
        pending = get_topics_by_status('pending')
        
        if not pending:
            return
        
        print("\nEnter topic names to reject (comma-separated):")
        choice = input(">> ").strip()
        
        topics_to_reject = [name.strip() for name in choice.split(',')]
        
        # For rejection, we'll just delete them from the database
        from admin.db_setup import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        
        rejected_count = 0
        for topic_name in topics_to_reject:
            try:
                cursor.execute('DELETE FROM topics WHERE name = ? AND status = ?', 
                             (topic_name, 'pending'))
                if cursor.rowcount > 0:
                    print(f"✓ Rejected: {topic_name}")
                    rejected_count += 1
                else:
                    print(f"✗ Topic not found or not pending: {topic_name}")
            except Exception as e:
                print(f"✗ Error rejecting {topic_name}: {e}")
        
        conn.commit()
        conn.close()
        print(f"\nTotal rejected: {rejected_count}/{len(topics_to_reject)}")
    
    def view_all_topics(self):
        """Display all topics with their statuses"""
        print("\n--- All Topics ---")
        topics = get_all_topics()
        
        if not topics:
            print("No topics found in the database.")
            return
        
        print(f"{'ID':<5} {'Topic Name':<30} {'Status':<12} {'Created At':<20}")
        print("-" * 70)
        for topic in topics:
            status_icon = {
                'pending': '⏳',
                'approved': '✓',
                'active': '🟢'
            }.get(topic['status'], '•')
            
            print(f"{topic['id']:<5} {topic['name']:<30} {status_icon} {topic['status']:<10} {topic['created_at']:<20}")
        
        # Summary
        pending_count = len([t for t in topics if t['status'] == 'pending'])
        approved_count = len([t for t in topics if t['status'] == 'approved'])
        active_count = len([t for t in topics if t['status'] == 'active'])
        
        print("\n" + "-" * 70)
        print(f"Summary: {pending_count} pending | {approved_count} approved | {active_count} active | {len(topics)} total")
    
    def view_subscriptions(self):
        """Display all user subscriptions"""
        print("\n--- User Subscriptions ---")
        subscriptions = get_all_subscriptions()
        
        if not subscriptions:
            print("No subscriptions found.")
            return
        
        print(f"{'User ID':<10} {'Topic Name':<30} {'Subscribed At':<20}")
        print("-" * 65)
        for sub in subscriptions:
            print(f"{sub['user_id']:<10} {sub['topic_name']:<30} {sub['subscribed_at']:<20}")
        
        # Group by user
        user_topics = {}
        for sub in subscriptions:
            user_id = sub['user_id']
            if user_id not in user_topics:
                user_topics[user_id] = []
            user_topics[user_id].append(sub['topic_name'])
        
        print("\n--- Subscription Summary ---")
        for user_id, topics in sorted(user_topics.items()):
            print(f"User {user_id}: {len(topics)} topics - {', '.join(topics)}")
    
    def run(self):
        """Run the admin panel"""
        print("\n🚀 Starting Admin Panel...")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.view_pending_topics()
            elif choice == '2':
                self.approve_topics()
            elif choice == '3':
                self.reject_topics()
            elif choice == '4':
                self.view_all_topics()
            elif choice == '5':
                self.view_subscriptions()
            elif choice == '6':
                print("\n👋 Exiting Admin Panel. Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please select 1-6.")
            
            input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    admin = AdminPanel()
    admin.run()

if __name__ == '__main__':
    main()
