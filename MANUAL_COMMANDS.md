# 📋 Manual Commands Guide - Kafka Dynamic Stream

This guide provides all commands needed to run the system on different machines/systems.

---

## 🗄️ **PREREQUISITES - MySQL Database Setup**

### Install MySQL Server

Choose one system to run the MySQL database (can be any of the systems):

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# On macOS
brew install mysql

# Start MySQL service
# Ubuntu/Debian:
sudo systemctl start mysql
sudo systemctl enable mysql

# macOS:
brew services start mysql
```

### Configure MySQL Database

```bash
# Login to MySQL as root
sudo mysql -u root -p

# Create database and user
CREATE DATABASE kafka_stream;
CREATE USER 'kafka_user'@'%' IDENTIFIED BY 'kafka_password';
GRANT ALL PRIVILEGES ON kafka_stream.* TO 'kafka_user'@'%';
FLUSH PRIVILEGES;
EXIT;

# If connecting from remote machines, edit MySQL config to allow remote connections
# Edit /etc/mysql/mysql.conf.d/mysqld.cnf (Ubuntu) or /usr/local/etc/my.cnf (macOS)
# Change: bind-address = 0.0.0.0

# Restart MySQL
sudo systemctl restart mysql  # Ubuntu
brew services restart mysql   # macOS
```

### Update config.json

On **ALL systems**, update `config.json` with MySQL connection details:

```json
{
  "bootstrap_servers": "KAFKA_BROKER_IP:9092",
  "mysql": {
    "host": "MYSQL_SERVER_IP",
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "kafka_password"
  }
}
```

**Replace:**
- `KAFKA_BROKER_IP` with the IP address of your Kafka broker machine
- `MYSQL_SERVER_IP` with the IP address of your MySQL database machine

### Initialize Database Schema

Run this **ONCE** from any system with the project files:

```bash
cd /path/to/kafka-dynamic-stream
python3 admin/db_setup.py
```

---

## 📦 **SYSTEM 1 - ZooKeeper Server**

### Prerequisites
- Java 8 or higher
- Apache Kafka installed at `/opt/kafka`

### Commands

```bash
# Navigate to Kafka directory
cd /opt/kafka

# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties
```

**Keep this terminal running.**

---

## 📦 **SYSTEM 2 - Kafka Broker + Topic Manager**

### Prerequisites
- Java 8 or higher
- Apache Kafka installed at `/opt/kafka`
- Python 3.12+
- Project files
- MySQL client connectivity

### Setup

```bash
# Install Python dependencies
cd /path/to/kafka-dynamic-stream
pip3 install -r requirements.txt

# Verify MySQL connection
python3 -c "from admin.db_setup import get_connection; conn = get_connection(); print('✓ MySQL connected'); conn.close()"
```

### Commands

**Terminal 1 - Kafka Broker:**
```bash
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties
```

**Terminal 2 - Topic Manager (on same system):**
```bash
cd /path/to/kafka-dynamic-stream
python3 broker/topic_manager.py
```

**Both terminals must keep running.**

---

## 📦 **SYSTEM 3 - Admin Panel**

### Prerequisites
- Python 3.12+
- Project files
- MySQL client connectivity

### Setup

```bash
cd /path/to/kafka-dynamic-stream
pip3 install -r requirements.txt
```

### Commands

```bash
cd /path/to/kafka-dynamic-stream
python3 admin/admin_panel.py
```

**Interactive Menu:**
- `1` - View pending topics
- `2` - Approve topics
- `3` - Reject topics
- `4` - Deactivate topics (mark for deletion)
- `5` - View all topics
- `6` - View subscriptions
- `7` - Exit

---

## 📦 **SYSTEM 4 - Producer**

### Prerequisites
- Python 3.12+
- Project files
- MySQL client connectivity
- Network access to Kafka broker

### Setup

```bash
cd /path/to/kafka-dynamic-stream
pip3 install -r requirements.txt
```

### Commands

```bash
cd /path/to/kafka-dynamic-stream
python3 producer/producer.py
```

**Interactive Commands:**
```
create <topic_name>              # Request new topic creation
send <topic_name> <message>      # Send message to topic
list                             # List all topics
active                           # List active topics
help                             # Show help
quit                             # Exit
```

**Example:**
```
> create news_updates
> send news_updates Breaking news from the producer!
```

---

## 📦 **SYSTEM 5 - Consumer (User 1)**

### Prerequisites
- Python 3.12+
- Project files
- MySQL client connectivity
- Network access to Kafka broker

### Setup

```bash
cd /path/to/kafka-dynamic-stream
pip3 install -r requirements.txt
```

### Commands

```bash
cd /path/to/kafka-dynamic-stream
python3 consumer/consumer.py 1
```

**Interactive Commands:**
```
list                            # List all active topics
subscribed                      # Show subscribed topics
subscribe <topic1> <topic2>     # Subscribe to topics
unsubscribe <topic>             # Unsubscribe from topic
refresh                         # Refresh subscriptions
help                            # Show help
quit                            # Exit
```

---

## 📦 **SYSTEM 6 - Consumer (User 2)**

Same as System 5, but use user ID `2`:

```bash
cd /path/to/kafka-dynamic-stream
python3 consumer/consumer.py 2
```

---

## 📦 **SYSTEM 7 - Web Dashboard (Optional)**

### Prerequisites
- Python 3.12+
- Project files (web/)
- MySQL client connectivity

### Setup

```bash
cd /path/to/kafka-dynamic-stream
pip3 install -r requirements.txt
```

### Commands

```bash
cd /path/to/kafka-dynamic-stream
python3 web/app.py
```

Then open in browser: **http://SERVER_IP:5000**

---

## 🔄 **Complete Workflow Example**

### Step 1: Start Infrastructure (Systems 1-2)

**System 1 (ZooKeeper):**
```bash
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

Wait 10 seconds, then...

**System 2 Terminal 1 (Kafka):**
```bash
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties
```

Wait 15 seconds, then...

**System 2 Terminal 2 (Topic Manager):**
```bash
cd /path/to/kafka-dynamic-stream
python3 broker/topic_manager.py
```

### Step 2: Start Admin Panel (System 3)

```bash
cd /path/to/kafka-dynamic-stream
python3 admin/admin_panel.py
```

### Step 3: Start Producer (System 4)

```bash
cd /path/to/kafka-dynamic-stream
python3 producer/producer.py
```

In producer terminal:
```
> create news_updates
✓ Topic 'news_updates' created with status: PENDING
```

### Step 4: Approve Topic (System 3 - Admin)

In admin panel:
```
Choose option: 2
Enter topic names: news_updates
✓ Approved: news_updates
```

**Broker Topic Manager (System 2) will automatically:**
- Detect approved topic
- Create it in Kafka
- Mark as ACTIVE

### Step 5: Start Consumer (System 5)

```bash
cd /path/to/kafka-dynamic-stream
python3 consumer/consumer.py 1
```

In consumer terminal:
```
> subscribe news_updates
✓ Subscribed to 'news_updates'
```

### Step 6: Send Message (System 4 - Producer)

```
> send news_updates Hello from distributed system!
✓ Message sent successfully
```

### Step 7: Receive Message (System 5 - Consumer)

Consumer terminal automatically displays:
```
📨 [news_updates] Message received:
   Hello from distributed system!
   Timestamp: 2025-11-07 15:30:45
```

---

## 🛠️ **Troubleshooting**

### MySQL Connection Issues

```bash
# Test MySQL connection
python3 -c "from admin.db_setup import get_connection; conn = get_connection(); print('✓ Connected'); conn.close()"

# Check MySQL is listening on all interfaces
sudo netstat -tlnp | grep 3306

# Check firewall allows MySQL port
sudo ufw allow 3306  # Ubuntu
```

### Kafka Connection Issues

```bash
# Test Kafka connection
python3 -c "from kafka import KafkaProducer; p = KafkaProducer(bootstrap_servers='BROKER_IP:9092'); print('✓ Connected'); p.close()"

# Verify Kafka is listening
netstat -tlnp | grep 9092

# Check Kafka logs
tail -f /opt/kafka/logs/server.log
```

### Topic Not Created

1. Check admin panel approved the topic
2. Check broker/topic_manager.py is running
3. Check MySQL database: `SELECT * FROM topics;`
4. Check Kafka: `/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092`

---

## 📊 **System Architecture**

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  System 1   │     │   System 2   │     │  System 3   │
│ ZooKeeper   │────→│ Kafka Broker │     │Admin Panel  │
└─────────────┘     │ + Topic Mgr  │     └─────────────┘
                    └──────────────┘            ↓
                           ↓                    ↓
                    ┌──────────────┐     ┌─────────────┐
                    │  MySQL DB    │←────│ All Systems │
                    │  (Any System)│     │  Connect    │
                    └──────────────┘     └─────────────┘
                           ↑
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  System 4   │    │  System 5   │    │  System 6   │
│  Producer   │    │ Consumer 1  │    │ Consumer 2  │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 🔐 **Security Notes**

1. **MySQL Security:**
   - Change default password in `config.json`
   - Use strong passwords in production
   - Restrict MySQL user permissions if needed

2. **Network Security:**
   - Use firewall rules to restrict access
   - Consider VPN for distributed deployment
   - Use SSL/TLS for MySQL connections in production

3. **Kafka Security:**
   - Configure Kafka ACLs if needed
   - Enable SSL for Kafka connections
   - Use SASL authentication in production

---

## 📝 **Notes**

- **MySQL Database:** Can run on any system, all other systems connect to it
- **Topic Manager:** Must run on same system as Kafka Broker (System 2)
- **Port Requirements:**
  - MySQL: 3306
  - ZooKeeper: 2181
  - Kafka: 9092
  - Web UI: 5000
- **Startup Order:** ZooKeeper → Kafka → Topic Manager → Others (any order)

---

**Last Updated:** November 7, 2025  
**Version:** 3.0 - MySQL + Manual Commands
