"""
Database Setup Module
This module initializes the MySQL database with required tables for managing
topics and user subscriptions in the dynamic Kafka streaming system.

Tables:
- topics: Stores topic metadata and approval status
- user_subscriptions: Maps users to their subscribed topics
"""

import mysql.connector
from mysql.connector import Error
import os
import json

# Load database configuration
def load_db_config():
    """Load database configuration from config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('mysql', {
                'host': 'localhost',
                'port': 3306,
                'database': 'kafka_stream',
                'user': 'kafka_user',
                'password': 'kafka_password'
            })
    except Exception as e:
        print(f"Error loading config: {e}")
        return {
            'host': 'localhost',
            'port': 3306,
            'database': 'kafka_stream',
            'user': 'kafka_user',
            'password': 'kafka_password'
        }

def initialize_database():
    """
    Initialize the MySQL database with required tables.
    Creates topics and user_subscriptions tables if they don't exist.
    """
    db_config = load_db_config()
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        cursor.execute(f"USE {db_config['database']}")
        
        # Create topics table
        # Status can be: 'pending', 'approved', 'active', 'inactive', 'deleted'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                status ENUM('pending', 'approved', 'active', 'inactive', 'deleted') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_status (status),
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Create user_subscriptions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                user_id INT NOT NULL,
                topic_name VARCHAR(255) NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(user_id, topic_name),
                FOREIGN KEY(topic_name) REFERENCES topics(name) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        conn.commit()
        print(f"✓ MySQL database initialized successfully: {db_config['host']}:{db_config['port']}/{db_config['database']}")
        
    except Error as e:
        print(f"✗ Error initializing MySQL database: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_connection():
    """
    Get a connection to the database.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
    """
    db_config = load_db_config()
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        return conn
    except Error as e:
        print(f"✗ Error connecting to MySQL database: {e}")
        raise


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
        cursor.execute('INSERT INTO topics (name, status) VALUES (%s, %s)', 
                      (topic_name, status))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        if e.errno == 1062:  # Duplicate entry error
            print(f"Topic '{topic_name}' already exists.")
        else:
            print(f"Error adding topic: {e}")
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, status, created_at FROM topics WHERE status = %s', 
                  (status,))
    topics = cursor.fetchall()
    cursor.close()
    conn.close()
    return topics

def get_all_topics():
    """
    Retrieve all topics from the database.
    
    Returns:
        list: List of all topic dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, name, status, created_at FROM topics ORDER BY created_at DESC')
    topics = cursor.fetchall()
    cursor.close()
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
            SET status = %s
            WHERE name = %s
        ''', (new_status, topic_name))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
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
        cursor.execute('INSERT INTO user_subscriptions (user_id, topic_name) VALUES (%s, %s)',
                      (user_id, topic_name))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        if e.errno == 1062:  # Duplicate entry error
            print(f"User {user_id} is already subscribed to {topic_name}")
        else:
            print(f"Error subscribing user: {e}")
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
        cursor.execute('DELETE FROM user_subscriptions WHERE user_id = %s AND topic_name = %s',
                      (user_id, topic_name))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
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
    cursor.execute('SELECT topic_name FROM user_subscriptions WHERE user_id = %s', 
                  (user_id,))
    topics = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return topics

def get_all_subscriptions():
    """
    Get all user subscriptions.
    
    Returns:
        list: List of subscription dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT user_id, topic_name, subscribed_at FROM user_subscriptions ORDER BY user_id')
    subscriptions = cursor.fetchall()
    cursor.close()
    conn.close()
    return subscriptions

if __name__ == '__main__':
    # Initialize the database
    initialize_database()
    print("\n✓ Database setup complete!")
    print("\nMake sure MySQL server is running and configured in config.json:")
    print("  - host: MySQL server hostname")
    print("  - port: MySQL server port (default 3306)")
    print("  - database: Database name (will be created if not exists)")
    print("  - user: MySQL username")
    print("  - password: MySQL password")
    
    # Add some sample topics for testing
    print("\n--- Adding Sample Topics ---")
    add_topic('news_updates', 'pending')
    add_topic('weather_data', 'pending')
    add_topic('stock_prices', 'pending')
    
    print("\n--- Current Topics ---")
    for topic in get_all_topics():
        print(f"  {topic['name']} [{topic['status']}]")
