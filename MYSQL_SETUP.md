# 🗄️ MySQL Database Setup Guide

This guide explains how to set up MySQL for the Kafka Dynamic Stream project.

---

## 📋 **Overview**

The system now uses **MySQL** instead of SQLite for:
- ✅ Better support for distributed deployments
- ✅ Concurrent access from multiple systems
- ✅ Better performance and scalability
- ✅ Remote database access

---

## 🚀 **Quick Start**

### 1. Install MySQL Server

Choose **ONE system** to run MySQL (can be any machine in your network).

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### macOS:
```bash
brew install mysql
brew services start mysql
```

#### Red Hat/CentOS:
```bash
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### 2. Secure MySQL Installation

```bash
sudo mysql_secure_installation
```

Follow prompts:
- Set root password
- Remove anonymous users
- Disallow root login remotely
- Remove test database
- Reload privilege tables

### 3. Create Database and User

```bash
# Login to MySQL as root
sudo mysql -u root -p

# Run these SQL commands
CREATE DATABASE kafka_stream CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'kafka_user'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON kafka_stream.* TO 'kafka_user'@'%';
FLUSH PRIVILEGES;
EXIT;
```

**Security Note:** Replace `'your_secure_password'` with a strong password!

### 4. Configure Remote Access (if needed)

If you need to access MySQL from other machines:

```bash
# Edit MySQL configuration
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf  # Ubuntu/Debian
# OR
sudo nano /etc/my.cnf  # Red Hat/CentOS
# OR
nano /usr/local/etc/my.cnf  # macOS

# Find and change:
bind-address = 0.0.0.0

# Save and exit (Ctrl+X, Y, Enter)

# Restart MySQL
sudo systemctl restart mysql  # Linux
brew services restart mysql   # macOS
```

### 5. Configure Firewall (Linux)

```bash
# Allow MySQL port
sudo ufw allow 3306
sudo ufw reload
```

### 6. Update config.json

On **ALL systems** that will connect to MySQL, update `config.json`:

```json
{
  "bootstrap_servers": "KAFKA_BROKER_IP:9092",
  "mysql": {
    "host": "MYSQL_SERVER_IP",
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "your_secure_password"
  }
}
```

**Replace:**
- `MYSQL_SERVER_IP` - IP address of MySQL server machine
- `KAFKA_BROKER_IP` - IP address of Kafka broker machine  
- `your_secure_password` - The password you set in step 3

### 7. Initialize Database Schema

From **any system** with the project files:

```bash
cd /path/to/kafka-dynamic-stream

# Install Python dependencies (includes mysql-connector-python)
pip3 install -r requirements.txt

# Initialize database tables
python3 admin/db_setup.py
```

You should see:
```
✓ MySQL database initialized successfully: YOUR_HOST:3306/kafka_stream
```

---

## 🔍 **Verify Setup**

### Test MySQL Connection

```bash
# From MySQL server
mysql -u kafka_user -p
# Enter password when prompted
USE kafka_stream;
SHOW TABLES;
# You should see: topics, user_subscriptions
EXIT;
```

### Test Remote Connection

From any other system:

```bash
mysql -h MYSQL_SERVER_IP -u kafka_user -p
# Enter password
USE kafka_stream;
SHOW TABLES;
EXIT;
```

### Test Python Connection

```bash
cd /path/to/kafka-dynamic-stream
python3 -c "from admin.db_setup import get_connection; conn = get_connection(); print('✓ MySQL Connected Successfully'); conn.close()"
```

---

## 📊 **Database Schema**

### topics table
```sql
CREATE TABLE topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    status ENUM('pending', 'approved', 'active', 'inactive', 'deleted') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### user_subscriptions table
```sql
CREATE TABLE user_subscriptions (
    user_id INT NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, topic_name),
    FOREIGN KEY(topic_name) REFERENCES topics(name) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 🛠️ **Troubleshooting**

### Connection Refused Error

```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
brew services list | grep mysql  # macOS

# Check MySQL is listening on port 3306
sudo netstat -tlnp | grep 3306
# OR
sudo ss -tlnp | grep 3306
```

### Access Denied Error

```bash
# Verify user permissions
sudo mysql -u root -p
SELECT user, host FROM mysql.user WHERE user='kafka_user';
SHOW GRANTS FOR 'kafka_user'@'%';
EXIT;

# If user doesn't exist or has wrong permissions, recreate:
DROP USER IF EXISTS 'kafka_user'@'%';
CREATE USER 'kafka_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON kafka_stream.* TO 'kafka_user'@'%';
FLUSH PRIVILEGES;
```

### Can't Connect from Remote Host

```bash
# Check bind-address in MySQL config
grep bind-address /etc/mysql/mysql.conf.d/mysqld.cnf

# Should be: bind-address = 0.0.0.0
# If not, edit and restart MySQL

# Check firewall
sudo ufw status
sudo ufw allow 3306

# Check if SELinux is blocking (Red Hat/CentOS)
sudo setsebool -P mysql_connect_any 1
```

### Import Error: mysql.connector

```bash
# Install MySQL connector
pip3 install mysql-connector-python==8.2.0

# OR upgrade pip and retry
pip3 install --upgrade pip
pip3 install mysql-connector-python
```

---

## 📈 **Performance Tuning (Optional)**

For better performance with multiple connections:

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

Add/modify:
```ini
[mysqld]
max_connections = 200
innodb_buffer_pool_size = 256M
query_cache_size = 32M
query_cache_limit = 2M
```

Restart MySQL:
```bash
sudo systemctl restart mysql
```

---

## 🔐 **Security Best Practices**

1. **Use Strong Passwords**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

2. **Restrict User Access**
   ```sql
   -- Instead of '%', use specific IPs
   CREATE USER 'kafka_user'@'192.168.1.%' IDENTIFIED BY 'password';
   ```

3. **Enable SSL/TLS** (Production)
   ```sql
   GRANT ALL PRIVILEGES ON kafka_stream.* TO 'kafka_user'@'%' REQUIRE SSL;
   ```

4. **Regular Backups**
   ```bash
   mysqldump -u kafka_user -p kafka_stream > backup.sql
   ```

5. **Monitor Logs**
   ```bash
   sudo tail -f /var/log/mysql/error.log
   ```

---

## 📝 **Useful MySQL Commands**

```sql
-- Show all databases
SHOW DATABASES;

-- Use kafka_stream database
USE kafka_stream;

-- Show all tables
SHOW TABLES;

-- View topics
SELECT * FROM topics;

-- View subscriptions
SELECT * FROM user_subscriptions;

-- Check topic counts by status
SELECT status, COUNT(*) FROM topics GROUP BY status;

-- View active topics
SELECT name, created_at FROM topics WHERE status='active';

-- Manual topic approval (for testing)
UPDATE topics SET status='approved' WHERE name='test_topic';

-- Delete old deleted topics
DELETE FROM topics WHERE status='deleted' AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

---

## 🔄 **Migration from SQLite**

If you have existing SQLite data to migrate:

```bash
# Export from SQLite
sqlite3 topics.db <<EOF
.headers on
.mode csv
.output topics.csv
SELECT * FROM topics;
.output user_subscriptions.csv
SELECT * FROM user_subscriptions;
.quit
EOF

# Import to MySQL
mysql -u kafka_user -p kafka_stream <<EOF
LOAD DATA LOCAL INFILE 'topics.csv' 
INTO TABLE topics 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;

LOAD DATA LOCAL INFILE 'user_subscriptions.csv' 
INTO TABLE user_subscriptions 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n' 
IGNORE 1 ROWS;
EOF
```

---

## 🆘 **Support**

If you encounter issues:

1. Check MySQL error logs: `/var/log/mysql/error.log`
2. Verify network connectivity: `ping MYSQL_SERVER_IP`
3. Test port accessibility: `telnet MYSQL_SERVER_IP 3306`
4. Check Python MySQL connector: `pip3 show mysql-connector-python`

---

**Last Updated:** November 7, 2025  
**MySQL Version:** 8.0+  
**Python Connector:** mysql-connector-python 8.2.0
