"""
Database Setup Module
This module initializes the SQLite database with required tables for managing
topics and user subscriptions in the dynamic Kafka streaming system.

Tables:
- topics: Stores topic metadata and approval status
- user_subscriptions: Maps users to their subscribed topics
"""

import sqlite3
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'topics.db')

def initialize_database():
    """
    Initialize the SQLite database with required tables.
    Creates topics and user_subscriptions tables if they don't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create topics table
    # Status can be: 'pending', 'approved', 'active'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'active')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            user_id INTEGER NOT NULL,
            topic_name TEXT NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, topic_name),
            FOREIGN KEY(topic_name) REFERENCES topics(name)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized successfully at: {DB_PATH}")

def get_connection():
    """
    Get a connection to the database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect(DB_PATH)

def add_topic(topic_name, status='pending'):
    """
    Add a new topic to the database.
    
    Args:
        topic_name (str): Name of the topic
        status (str): Initial status (default: 'pending')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO topics (name, status) VALUES (?, ?)', 
                      (topic_name, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        print(f"Topic '{topic_name}' already exists.")
        return False
    except Exception as e:
        print(f"Error adding topic: {e}")
        return False

def get_topics_by_status(status):
    """
    Retrieve all topics with a specific status.
    
    Args:
        status (str): Status to filter by ('pending', 'approved', 'active')
    
    Returns:
        list: List of topic dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, status, created_at FROM topics WHERE status = ?', 
                  (status,))
    topics = []
    for row in cursor.fetchall():
        topics.append({
            'id': row[0],
            'name': row[1],
            'status': row[2],
            'created_at': row[3]
        })
    conn.close()
    return topics

def get_all_topics():
    """
    Retrieve all topics from the database.
    
    Returns:
        list: List of all topic dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, status, created_at FROM topics ORDER BY created_at DESC')
    topics = []
    for row in cursor.fetchall():
        topics.append({
            'id': row[0],
            'name': row[1],
            'status': row[2],
            'created_at': row[3]
        })
    conn.close()
    return topics

def update_topic_status(topic_name, new_status):
    """
    Update the status of a topic.
    
    Args:
        topic_name (str): Name of the topic
        new_status (str): New status value
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE topics 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE name = ?
        ''', (new_status, topic_name))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"Error updating topic status: {e}")
        return False

def subscribe_user_to_topic(user_id, topic_name):
    """
    Subscribe a user to a topic.
    
    Args:
        user_id (int): User identifier
        topic_name (str): Name of the topic
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO user_subscriptions (user_id, topic_name) VALUES (?, ?)',
                      (user_id, topic_name))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        print(f"User {user_id} is already subscribed to {topic_name}")
        return False
    except Exception as e:
        print(f"Error subscribing user: {e}")
        return False

def unsubscribe_user_from_topic(user_id, topic_name):
    """
    Unsubscribe a user from a topic.
    
    Args:
        user_id (int): User identifier
        topic_name (str): Name of the topic
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_subscriptions WHERE user_id = ? AND topic_name = ?',
                      (user_id, topic_name))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0
    except Exception as e:
        print(f"Error unsubscribing user: {e}")
        return False

def get_user_subscriptions(user_id):
    """
    Get all topics a user is subscribed to.
    
    Args:
        user_id (int): User identifier
    
    Returns:
        list: List of topic names
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT topic_name FROM user_subscriptions WHERE user_id = ?', 
                  (user_id,))
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    return topics

def get_all_subscriptions():
    """
    Get all user subscriptions.
    
    Returns:
        list: List of subscription dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, topic_name, subscribed_at FROM user_subscriptions ORDER BY user_id')
    subscriptions = []
    for row in cursor.fetchall():
        subscriptions.append({
            'user_id': row[0],
            'topic_name': row[1],
            'subscribed_at': row[2]
        })
    conn.close()
    return subscriptions

if __name__ == '__main__':
    # Initialize the database
    initialize_database()
    
    # Add some sample topics for testing
    print("\n--- Adding Sample Topics ---")
    add_topic('news_updates', 'pending')
    add_topic('weather_data', 'pending')
    add_topic('stock_prices', 'pending')
    
    print("\n--- Current Topics ---")
    for topic in get_all_topics():
        print(f"  {topic['name']} [{topic['status']}]")
