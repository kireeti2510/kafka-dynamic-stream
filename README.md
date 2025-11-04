# 🚀 Kafka Dynamic Content Stream

A real-time, adaptive content streaming platform that integrates Kafka message broker, dynamic topic management, and multi-threaded producer-consumer architecture.

## 📋 Project Overview

This project simulates a dynamic Kafka-based content streaming system where:
- **Topics can be created, approved, and activated in real-time**
- **Producers dynamically publish to active topics**
- **Consumers dynamically subscribe to topics of interest**
- **A centralized database manages topic metadata and user subscriptions**
- **A web UI displays real-time system status**

## 🏗️ Architecture

```
┌─────────────────┐
│  Admin Panel    │ ──> Approves/Rejects Topics
│  + Database     │
└────────┬────────┘
         │
         │ (DB: pending → approved → active)
         │
         ↓
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Producer Node  │ ───> │ Kafka Broker │ ───> │ Consumer Node   │
│  (3 Threads)    │      │              │      │ (Dynamic Sub)   │
└─────────────────┘      └──────────────┘      └─────────────────┘
│                                                        │
├─ Publisher Thread ────────────────────────────────────┤
├─ Topic Watcher Thread                                 │
└─ Input Listener Thread                                │
                                                         │
                                           ┌─────────────┴─────────┐
                                           │     Web UI (Flask)    │
                                           │  Shows Topics & Subs  │
                                           └───────────────────────┘
```

## 🗂️ Project Structure

```
kafka_dynamic_stream/
│
├── config.json              # Kafka configuration
├── requirements.txt         # Python dependencies
├── topics.db               # SQLite database (auto-created)
├── kafka_env_setup.py      # Kafka environment validation module
│
├── admin/
│   ├── db_setup.py         # Database initialization and queries
│   └── admin_panel.py      # Interactive CLI for topic approval
│
├── producer/
│   ├── producer.py         # Multi-threaded producer coordinator
│   ├── topic_watcher.py    # Monitors approved topics, creates in Kafka
│   └── input_listener.py   # Accepts user input for topics/messages
│
├── consumer/
│   └── consumer.py         # Dynamic consumer with subscription management
│
└── web/
    └── app.py              # Flask web UI for visualization
```

## 📦 Database Schema

### Topics Table
```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    status TEXT CHECK(status IN ('pending', 'approved', 'active')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### User Subscriptions Table
```sql
CREATE TABLE user_subscriptions (
    user_id INTEGER NOT NULL,
    topic_name TEXT NOT NULL,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, topic_name),
    FOREIGN KEY(topic_name) REFERENCES topics(name)
)
```

## 🔧 Setup Instructions

### 1. Prerequisites

- **Python 3.7+** installed
- **Apache Kafka** installed at `/opt/kafka`
- **Java** (required for Kafka)

### 2. Install Python Dependencies

```bash
cd /home/pes1ug23cs307/kafka_dynamic_stream
pip3 install -r requirements.txt
```

### 3. Start Kafka Infrastructure

**Terminal 1 - Start Zookeeper:**
```bash
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

**Terminal 2 - Start Kafka Broker:**
```bash
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties
```

**Important:** Ensure `auto.create.topics.enable=false` in `server.properties`

### 4. Initialize Database

```bash
python3 admin/db_setup.py
```

This creates `topics.db` with required tables.

### 5. Validate Kafka Environment (Optional but Recommended)

```bash
python3 kafka_env_setup.py
```

This performs comprehensive checks:
- ✅ Kafka installation detection
- ✅ Service status validation (ZooKeeper & Kafka)
- ✅ Broker connection testing
- ✅ Configuration file reading
- ✅ Admin API verification

**Note:** Producer and Consumer automatically run this validation on startup!

## 🚀 Usage Guide

> **⚡ Quick Tip:** The system now includes automatic Kafka environment validation. If services are not running, you'll see clear instructions on how to start them.

### Step 1: Start Admin Panel

```bash
python3 admin/admin_panel.py
```

**Admin Panel Commands:**
- `1` - View pending topics
- `2` - Approve topics (moves to 'approved' status)
- `3` - Reject topics
- `4` - View all topics
- `5` - View user subscriptions
- `6` - Exit

### Step 2: Start Producer

```bash
python3 producer/producer.py
```

**Producer Threads:**
1. **Publisher Thread** - Publishes messages from queue to Kafka
2. **Topic Watcher Thread** - Monitors approved topics, creates them in Kafka (approved → active)
3. **Input Listener Thread** - Interactive CLI for user input

**Producer Commands:**
```
create <topic_name>              # Create new topic (status: pending)
send <topic_name> <message>      # Send message to active topic
list                             # List all topics with statuses
active                           # List only active topics
help                             # Show help menu
quit                             # Exit producer
```

### Step 3: Start Consumer(s)

**Consumer 1 (User ID: 1):**
```bash
python3 consumer/consumer.py 1
```

**Consumer 2 (User ID: 2):**
```bash
python3 consumer/consumer.py 2
```

**Consumer Commands:**
```
list                              # List all active topics
subscribed                        # Show your subscribed topics
subscribe <topic1> <topic2> ...   # Subscribe to topics
unsubscribe <topic1> <topic2> ... # Unsubscribe from topics
refresh                           # Refresh subscription from DB
help                              # Show help menu
quit                              # Exit consumer
```

### Step 4: Start Web UI (Optional)

```bash
python3 web/app.py
```

Visit: **http://localhost:5000**

**Web UI Features:**
- Real-time topic status visualization
- User subscription mapping
- Auto-refreshes every 5 seconds
- System statistics dashboard

## 📖 Complete Workflow Example

### Scenario: Creating and Consuming a News Topic

**1. Producer Terminal:**
```bash
$ python3 producer/producer.py
> create news_updates
✓ Topic 'news_updates' created with status: PENDING
```

**2. Admin Terminal:**
```bash
$ python3 admin/admin_panel.py
Choice: 2 (Approve Topics)
Enter topic names: news_updates
✓ Approved: news_updates
```

**3. Producer Terminal (automatic):**
```
📋 Topic Watcher: Found 1 approved topic(s)
🔨 Topic Watcher: Processing 'news_updates'...
✓ Topic Watcher: Created Kafka topic 'news_updates'
✓ Topic Watcher: 'news_updates' is now ACTIVE
```

**4. Consumer Terminal:**
```bash
$ python3 consumer/consumer.py 1
> subscribe news_updates
✓ Subscribed to 'news_updates'
📋 Active subscriptions: news_updates
```

**5. Producer Terminal:**
```
> send news_updates Breaking: Major tech announcement!
✓ Message queued for topic 'news_updates'
✓ Publisher: Sent to 'news_updates' [partition 1, offset 0]
```

**6. Consumer Terminal (receives message):**
```
📨 [news_updates] Message received:
   Content: Breaking: Major tech announcement!
   Timestamp: 2025-11-04 14:30:45
   Partition: 1 | Offset: 0
```

## 🔑 Key Features

### ✅ Dynamic Topic Management
- Topics created via producer are stored as **'pending'**
- Admin approves/rejects topics → **'approved'**
- Topic Watcher creates them in Kafka → **'active'**

### ✅ Multi-threaded Producer
- **Publisher Thread**: Consumes from internal queue, sends to Kafka
- **Topic Watcher**: Polls DB every 5s for approved topics
- **Input Listener**: Non-blocking CLI for user interaction

### ✅ Dynamic Consumer Subscription
- Query DB for active topics
- Subscribe/unsubscribe at runtime
- Multiple consumers with unique user IDs
- Auto-commit enabled for reliability

### ✅ Centralized Metadata Store (SQLite)
- Single source of truth for topic states
- User-topic subscription mapping
- Timestamp tracking for auditing

### ✅ Web Dashboard
- Real-time visualization
- RESTful JSON APIs
- Clean, responsive UI
- Auto-refresh capability

## 🛠️ Configuration

Edit `config.json` to customize:

```json
{
  "bootstrap_servers": "localhost:9092",
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_watcher_poll_interval": 5,
  "acks": 1,
  "compression_type": "gzip",
  "retries": 3,
  "auto_offset_reset": "latest"
}
```

## 🧪 Testing the System

### Test 1: Create Multiple Topics
```bash
# Producer
> create weather_data
> create stock_prices
> create sports_updates

# Admin
Approve all topics

# Verify in Web UI
Visit http://localhost:5000
```

### Test 2: Multi-Consumer Scenario
```bash
# Terminal 1: Consumer User 1
python3 consumer/consumer.py 1
> subscribe weather_data stock_prices

# Terminal 2: Consumer User 2
python3 consumer/consumer.py 2
> subscribe stock_prices sports_updates

# Producer: Send messages
> send weather_data Sunny, 25°C
> send stock_prices AAPL: $150.23
> send sports_updates Lakers win 110-95

# Observe: User 1 gets weather + stock, User 2 gets stock + sports
```

### Test 3: Dynamic Subscription
```bash
# Consumer subscribed to 'news'
# Producer creates and activates 'tech_news'
# Consumer can subscribe without restart:
> list
> subscribe tech_news
```

## 🐛 Troubleshooting

### Issue: "Connection refused" to Kafka
**Solution:** Ensure Zookeeper and Kafka broker are running:
```bash
# Check if running
ps aux | grep kafka
ps aux | grep zookeeper

# Check Kafka logs
tail -f /opt/kafka/logs/server.log
```

### Issue: Topics not being created in Kafka
**Solution:** 
1. Check `auto.create.topics.enable=false` in Kafka config
2. Verify Topic Watcher is running in producer
3. Check admin approved the topic
4. View Topic Watcher logs in producer terminal

### Issue: Consumer not receiving messages
**Solution:**
1. Ensure topic is **'active'** (not pending/approved)
2. Verify consumer is subscribed: `> subscribed`
3. Check Kafka topic exists: `/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092`

### Issue: Web UI shows no data
**Solution:**
1. Verify database exists: `ls -la topics.db`
2. Check Flask logs for errors
3. Initialize DB: `python3 admin/db_setup.py`

## 📊 Monitoring Commands

### Check Kafka Topics
```bash
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Describe a Topic
```bash
/opt/kafka/bin/kafka-topics.sh --describe --topic news_updates --bootstrap-server localhost:9092
```

### View Database
```bash
sqlite3 topics.db
sqlite> SELECT * FROM topics;
sqlite> SELECT * FROM user_subscriptions;
sqlite> .exit
```

### Check Consumer Groups
```bash
/opt/kafka/bin/kafka-consumer-groups.sh --list --bootstrap-server localhost:9092
```

## 🎯 Project Highlights

- ✅ **Multi-threaded architecture** with proper synchronization
- ✅ **Real-time topic lifecycle management** (pending → approved → active)
- ✅ **Kafka Admin API integration** for programmatic topic creation
- ✅ **Dynamic subscription model** without restart requirement
- ✅ **RESTful web interface** for visualization
- ✅ **Scalable design** supporting multiple producers and consumers
- ✅ **Clean separation of concerns** across modules

## 📝 Technical Stack Summary

| Component | Technology |
|-----------|-----------|
| Message Broker | Apache Kafka 2.x+ |
| Language | Python 3.7+ |
| Database | SQLite 3 |
| Web Framework | Flask 3.0 |
| Kafka Client | kafka-python 2.0.2 |
| Threading | Python threading module |
| Serialization | JSON |

## 🎓 Learning Outcomes

This project demonstrates:
- Kafka Admin API usage for dynamic topic management
- Multi-threaded programming with producer-consumer patterns
- Database-driven control plane architecture
- Real-time stream processing
- Web-based monitoring and visualization
- Event-driven system design

## 📄 License

This is an educational project for learning Kafka and distributed systems concepts.

## 👨‍💻 Author

PES1UG23CS307

---

**Happy Streaming! 🚀**
