# 🚀 Kafka Dynamic Content Stream

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Apache Kafka](https://img.shields.io/badge/kafka-2.x+-orange.svg)](https://kafka.apache.org/)
[![MySQL](https://img.shields.io/badge/mysql-8.0+-blue.svg)](https://www.mysql.com/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time, adaptive content streaming platform demonstrating dynamic Kafka topic management, multi-threaded architecture, distributed database, and broker-side topic lifecycle control.

## 📋 Features

- ✅ **Dynamic Topic Creation** - Create topics at runtime without restarts
- ✅ **5-Stage Lifecycle** - pending → approved → active → inactive → deleted
- ✅ **Broker-Side Topic Management** - All topic operations via Kafka Admin API
- ✅ **Multi-threaded Producer** - Publisher, Input Listener
- ✅ **Dynamic Consumer Subscription** - Subscribe/unsubscribe in real-time
- ✅ **MySQL Database** - Centralized, distributed-ready metadata store
- ✅ **Distributed Architecture** - Run components on different machines
- ✅ **Web Dashboard** - Real-time visualization with auto-refresh
- ✅ **Admin API Integration** - Programmatic topic creation and deletion

## 🏗️ Architecture

```
┌──────────────┐
│ Admin Panel  │ → Approve/Deactivate Topics
│  + MySQL DB  │
└──────┬───────┘
       │ (pending → approved → active → inactive → deleted)
       ↓
┌─────────────┐    ┌──────────┐    ┌────────────┐
│  Producer   │ →  │  Kafka   │ →  │  Consumer  │
│ (2 threads) │    │  Broker  │    │ (Dynamic)  │
└─────────────┘    └────┬─────┘    └────────────┘
                        │
                 ┌──────┴──────┐
                 │Topic Manager│ ← Broker-side service
                 │(Admin API)  │   Creates/Deletes topics
                 └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Apache Kafka** with ZooKeeper
- **MySQL Server 8.0+**
- **Java 8+** (required for Kafka)
- **Network connectivity** between systems (for distributed setup)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream
```

### 2️⃣ Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 3️⃣ Setup MySQL Database

See **[MYSQL_SETUP.md](MYSQL_SETUP.md)** for detailed instructions.

**Quick setup:**
```bash
# Login to MySQL
sudo mysql -u root -p

# Create database and user
CREATE DATABASE kafka_stream;
CREATE USER 'kafka_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON kafka_stream.* TO 'kafka_user'@'%';
FLUSH PRIVILEGES;
EXIT;
```

### 4️⃣ Configure Application

Edit `config.json`:
```json
{
  "bootstrap_servers": "KAFKA_BROKER_IP:9092",
  "mysql": {
    "host": "MYSQL_SERVER_IP",
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "your_password"
  }
}
```

### 5️⃣ Initialize Database Schema

```bash
python3 admin/db_setup.py
```

### 6️⃣ Start Components

See **[MANUAL_COMMANDS.md](MANUAL_COMMANDS.md)** for detailed instructions on each system.

**Startup Order:**

1. **MySQL Server** (any system)
2. **ZooKeeper** (System 1):
   ```bash
   cd /opt/kafka
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

3. **Kafka Broker** (System 2):
   ```bash
   cd /opt/kafka
   bin/kafka-server-start.sh config/server.properties
   ```

4. **Topic Manager** (System 2 - same as broker):
   ```bash
   cd kafka-dynamic-stream
   python3 broker/topic_manager.py
   ```

5. **Admin Panel** (System 3):
   ```bash
   python3 admin/admin_panel.py
   ```

6. **Producer** (System 4):
   ```bash
   python3 producer/producer.py
   ```

7. **Consumer** (System 5+):
   ```bash
   python3 consumer/consumer.py 1
   ```

## 🎯 Complete Test Workflow

### 1. Create a Topic (Producer - System 4)
```
> create news_updates
✓ Topic 'news_updates' created with status: PENDING
```

### 2. Approve Topic (Admin - System 3)
```
Choose option: 2
Enter topic names: news_updates
✓ Approved: news_updates
```

### 3. Wait for Activation (Automatic - Broker System 2)
Broker Topic Manager detects approval and creates in Kafka:
```
✓ Topic Manager: Created Kafka topic 'news_updates'
✓ Topic Manager: 'news_updates' is now ACTIVE
```

### 4. Subscribe (Consumer - System 5)
```
> subscribe news_updates
✓ Subscribed to 'news_updates'
```

### 5. Send Message (Producer - System 4)
```
> send news_updates Hello from distributed system!
✓ Message sent
```

### 6. Receive Message (Consumer - System 5)
```
📨 [news_updates] Message received:
   Content: Hello from distributed system!
   Timestamp: 2025-11-07 15:30:45
```

### 7. Deactivate Topic (Admin - System 3)
```
Choose option: 4
Enter topic: news_updates
✓ Deactivated: news_updates (will be deleted from Kafka)
```

Broker Topic Manager automatically deletes it from Kafka.

## 📚 Project Structure

```
kafka_dynamic_stream/
│
├── config.json                   # Configuration (Kafka + MySQL)
├── requirements.txt              # Python dependencies
├── MANUAL_COMMANDS.md            # Manual commands for each system
├── MYSQL_SETUP.md                # MySQL installation guide
├── README.md                     # This file
│
├── broker/                       # Broker-side services
│   ├── topic_manager.py         # Topic lifecycle via Admin API
│   └── README.md                # Broker documentation
│
├── admin/
│   ├── db_setup.py              # MySQL database setup
│   └── admin_panel.py           # Topic approval/deactivation CLI
│
├── producer/
│   ├── producer.py              # Multi-threaded coordinator
│   ├── topic_watcher.py         # (Legacy) Topic watcher
│   └── input_listener.py        # User input handler
│
├── consumer/
│   └── consumer.py              # Dynamic subscription consumer
│
└── web/
    └── app.py                   # Flask dashboard
```
├── terminal5_consumer.sh         # Start Consumer
├── terminal6_webui.sh            # Start Web UI
│
├── config.json                   # Kafka configuration
├── requirements.txt              # Python dependencies
├── kafka_env_setup.py            # Environment validation
│
├── broker/                       # NEW! Broker-side services
│   ├── topic_manager.py         # Topic lifecycle via Admin API
│   └── README.md                # Broker documentation
│
├── admin/
│   ├── db_setup.py              # Database initialization
│   └── admin_panel.py           # Topic approval/deactivation CLI
│
├── producer/
│   ├── producer.py              # Multi-threaded coordinator
│   ├── topic_watcher.py         # (Legacy) Topic watcher
│   └── input_listener.py        # User input handler
│
├── consumer/
│   └── consumer.py              # Dynamic subscription consumer
│
└── web/
    └── app.py                   # Flask dashboard

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "bootstrap_servers": "KAFKA_BROKER_IP:9092",
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_manager_poll_interval": 5,
  "sync_orphaned_topics": false,
  "broker_id": 0,
  "mysql": {
    "host": "MYSQL_SERVER_IP",
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "your_password"
  }
}
```

**Kafka Parameters:**
- `bootstrap_servers`: Kafka broker address
- `topic_manager_poll_interval`: How often broker checks for topic changes (seconds)
- `sync_orphaned_topics`: Enable orphaned topic detection
- `broker_id`: Identifier for this broker instance

**MySQL Parameters:**
- `host`: MySQL server hostname/IP
- `port`: MySQL server port (default 3306)
- `database`: Database name
- `user`: MySQL username
- `password`: MySQL password

## 💻 Command Reference

### Producer Commands
- `create <topic>` - Create new topic
- `send <topic> <message>` - Send message
- `list` - List all topics
- `active` - List active topics
- `help` - Show help
- `quit` - Exit

### Consumer Commands
- `list` - List active topics
- `subscribed` - Show subscribed topics
- `subscribe <topic1> <topic2>` - Subscribe to topics
- `unsubscribe <topic>` - Unsubscribe from topic
- `refresh` - Refresh subscriptions
- `help` - Show help
- `quit` - Exit


### Admin Commands
- `1` - View pending topics
- `2` - Approve topics
- `3` - Reject topics
- `4` - Deactivate topics (mark for deletion)
- `5` - View all topics
- `6` - View subscriptions
- `7` - Exit

## 🛠️ Troubleshooting

### "Connection refused to MySQL"
**Solution:** 
1. Ensure MySQL server is running
2. Check `config.json` has correct MySQL host/credentials
3. Test connection: `python3 -c "from admin.db_setup import get_connection; get_connection()"`

### "Connection refused to Kafka"
**Solution:** 
1. Ensure ZooKeeper is running
2. Ensure Kafka Broker is running
3. Check `config.json` has correct bootstrap_servers

### "Topic not created in Kafka"
**Solution:** Check approval flow:
1. Producer creates → PENDING (check with admin panel option 1)
2. Admin approves → APPROVED (use admin panel option 2)
3. Broker Topic Manager creates → ACTIVE (automatic, check broker logs)
4. Verify MySQL: `SELECT * FROM topics;`

### "How to delete a topic?"
**Solution:** Use Admin Panel:
1. Run `python3 admin/admin_panel.py`
2. Choose option 4 (Deactivate Topics)
3. Enter topic name
4. Broker Topic Manager will delete it from Kafka automatically

### "Consumer not receiving messages"
**Solution:**
- Verify topic is ACTIVE: Check admin panel option 5
- Check consumer is subscribed: Use `subscribed` command
- Ensure producer sent to correct topic
- Verify MySQL connection for all components

### "ModuleNotFoundError: mysql.connector"
**Solution:** Install MySQL connector:
```bash
pip3 install mysql-connector-python==8.2.0
```

## 📖 Documentation

- **[MANUAL_COMMANDS.md](MANUAL_COMMANDS.md)** - Complete manual commands for all systems
- **[MYSQL_SETUP.md](MYSQL_SETUP.md)** - MySQL database installation and setup
- **[BROKER_LOCATION.md](BROKER_LOCATION.md)** - Topic management location guide
- **[BROKER_TOPIC_MANAGEMENT.md](BROKER_TOPIC_MANAGEMENT.md)** - Broker-side implementation
- **[broker/README.md](broker/README.md)** - Broker Topic Manager documentation
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration from SQLite to MySQL

## 🎓 Learning Outcomes

This project demonstrates:
- **Kafka Admin API** - Topic creation, deletion, management
- **Multi-threaded Python** - Concurrent producer/consumer patterns
- **Distributed Database** - MySQL for multi-system coordination
- **Producer-Consumer Patterns** - Real-time message streaming
- **Database-Driven Control** - Centralized topic lifecycle management
- **RESTful API Design** - Web dashboard integration
- **Broker-Side Architecture** - Separation of concerns
- **Distributed Systems** - Multi-machine deployment

## 🚀 Deployment Options

### Single Machine (Development)
Run all components on one machine using `localhost` for all IPs.

### Multi-Machine (Production)
- **System 1:** ZooKeeper
- **System 2:** Kafka Broker + Topic Manager
- **System 3:** MySQL Database + Admin Panel
- **System 4+:** Producers and Consumers

See [MANUAL_COMMANDS.md](MANUAL_COMMANDS.md) for detailed deployment instructions.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**PES1UG23CS307**

## 🙏 Acknowledgments

- Apache Kafka community
- Flask framework
- kafka-python-ng maintainers

---

**⭐ If you find this project helpful, please give it a star!**

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the documentation files
3. Open an issue on GitHub

---

Made with ❤️ for learning distributed systems and real-time streaming
