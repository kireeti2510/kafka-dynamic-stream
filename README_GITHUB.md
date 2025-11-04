# 🚀 Kafka Dynamic Content Stream

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Apache Kafka](https://img.shields.io/badge/kafka-2.x+-orange.svg)](https://kafka.apache.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time, adaptive content streaming platform demonstrating dynamic Kafka topic management, multi-threaded architecture, and database-driven control systems.

## 📋 Features

- ✅ **Dynamic Topic Creation** - Create topics at runtime without restarts
- ✅ **3-Stage Approval Workflow** - pending → approved → active
- ✅ **Multi-threaded Producer** - Publisher, Topic Watcher, Input Listener
- ✅ **Dynamic Consumer Subscription** - Subscribe/unsubscribe in real-time
- ✅ **Kafka Admin API Integration** - Programmatic topic management
- ✅ **SQLite Metadata Store** - Centralized control plane
- ✅ **Web Dashboard** - Real-time visualization with auto-refresh
- ✅ **Environment Validation** - Automatic Kafka health checks

## 🏗️ Architecture

```
┌──────────────┐
│ Admin Panel  │ → Approve/Reject Topics
│  + Database  │
└──────┬───────┘
       │ (pending → approved → active)
       ↓
┌─────────────┐    ┌──────────┐    ┌────────────┐
│  Producer   │ →  │  Kafka   │ →  │  Consumer  │
│ (3 threads) │    │  Broker  │    │ (Dynamic)  │
└─────────────┘    └──────────┘    └────────────┘
                                           │
                                    ┌──────┴───────┐
                                    │   Web UI     │
                                    │ (Dashboard)  │
                                    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Ubuntu/Debian Linux** (tested on Ubuntu 22.04+)
- **Python 3.12+**
- **Apache Kafka** installed at `/opt/kafka`
- **Java** (required for Kafka)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/kafka-dynamic-stream.git
cd kafka-dynamic-stream
```

### 2️⃣ Run Setup (One-Time)

```bash
./SETUP_ENVIRONMENT.sh
```

This script will:
- ✅ Check all prerequisites
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Initialize SQLite database
- ✅ Make terminal scripts executable

### 3️⃣ Start the System

Open **6 terminal windows** and run these scripts:

**Terminal 1 - ZooKeeper:**
```bash
./terminal1_zookeeper.sh
```

**Terminal 2 - Kafka Broker** (wait 10s after ZooKeeper):
```bash
./terminal2_kafka.sh
```

**Terminal 3 - Admin Panel** (after Kafka is ready):
```bash
./terminal3_admin.sh
```

**Terminal 4 - Producer:**
```bash
./terminal4_producer.sh
```

**Terminal 5 - Consumer:**
```bash
./terminal5_consumer.sh
```

**Terminal 6 - Web UI** (optional):
```bash
./terminal6_webui.sh
```
Then open: **http://localhost:5000**

## 🎯 Complete Test Workflow

### 1. Create a Topic (Producer)
```
> create news_updates
✓ Topic 'news_updates' created with status: PENDING
```

### 2. Approve Topic (Admin)
```
Choose option: 2
Enter topic names: news_updates
✓ Approved: news_updates
```

### 3. Wait for Activation (Automatic)
Topic Watcher detects approval and creates in Kafka:
```
✓ Topic Watcher: 'news_updates' is now ACTIVE
```

### 4. Subscribe (Consumer)
```
> subscribe news_updates
✓ Subscribed to 'news_updates'
```

### 5. Send Message (Producer)
```
> send news_updates Hello, this is a test message!
✓ Message sent
```

### 6. Receive Message (Consumer)
```
📨 [news_updates] Message received:
   Content: Hello, this is a test message!
   Timestamp: 2025-11-04 14:30:45
```

## 📚 Project Structure

```
kafka_dynamic_stream/
│
├── SETUP_ENVIRONMENT.sh      # One-time setup script
├── terminal1_zookeeper.sh    # Start ZooKeeper
├── terminal2_kafka.sh        # Start Kafka Broker
├── terminal3_admin.sh        # Start Admin Panel
├── terminal4_producer.sh     # Start Producer
├── terminal5_consumer.sh     # Start Consumer
├── terminal6_webui.sh        # Start Web UI
│
├── config.json               # Kafka configuration
├── requirements.txt          # Python dependencies
├── kafka_env_setup.py        # Environment validation
│
├── admin/
│   ├── db_setup.py          # Database initialization
│   └── admin_panel.py       # Topic approval CLI
│
├── producer/
│   ├── producer.py          # Multi-threaded coordinator
│   ├── topic_watcher.py     # Monitors & creates topics
│   └── input_listener.py    # User input handler
│
├── consumer/
│   └── consumer.py          # Dynamic subscription consumer
│
└── web/
    └── app.py               # Flask dashboard
```

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "bootstrap_servers": "localhost:9092",
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_watcher_poll_interval": 5
}
```

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
- `subscribed` - Show subscriptions
- `subscribe <topic1> <topic2>` - Subscribe
- `unsubscribe <topic1>` - Unsubscribe
- `refresh` - Reload from database
- `quit` - Exit

### Admin Commands
- `1` - View pending topics
- `2` - Approve topics
- `3` - Reject topics
- `4` - View all topics
- `5` - View subscriptions
- `6` - Exit

## 🛠️ Troubleshooting

### "Connection refused to Kafka"
**Solution:** Ensure ZooKeeper and Kafka Broker are running (terminals 1 & 2)

### "Topic not created in Kafka"
**Solution:** Check approval flow:
1. Producer creates → PENDING
2. Admin approves → APPROVED
3. Topic Watcher creates → ACTIVE

### "Consumer not receiving messages"
**Solution:**
- Verify topic is ACTIVE (not just approved)
- Check consumer is subscribed: `> subscribed`
- Ensure producer sent to correct topic

### "ModuleNotFoundError: kafka"
**Solution:** Run setup script:
```bash
./SETUP_ENVIRONMENT.sh
```

## 📖 Documentation

- **[KAFKA_ENV_SETUP.md](KAFKA_ENV_SETUP.md)** - Environment validation guide
- **[QUICK_REFERENCE.sh](QUICK_REFERENCE.sh)** - All commands reference
- **[ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md)** - Latest features

## 🎓 Learning Outcomes

This project demonstrates:
- Apache Kafka Admin API usage
- Multi-threaded Python programming
- Producer-consumer patterns
- Database-driven control systems
- RESTful API design
- Real-time streaming architecture
- Web-based monitoring

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

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
