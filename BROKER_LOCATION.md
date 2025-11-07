# 📍 WHERE IS TOPIC CREATION/DEACTIVATION VIA ADMIN API?

## 🎯 Answer: In the Kafka Broker

All topic lifecycle management via Kafka Admin API is now handled in:

```
/broker/topic_manager.py  ← THIS IS YOUR MAIN FILE
```

---

## 📂 Complete File Structure

```
kafka-dynamic-stream/
│
├── broker/                              ← NEW FOLDER!
│   ├── topic_manager.py                 ← ⭐ MAIN TOPIC MANAGEMENT SERVICE
│   └── README.md                        ← Documentation
│
├── admin/
│   ├── admin_panel.py                   ← Updated: Added deactivation option
│   └── db_setup.py                      ← Updated: Added inactive/deleted statuses
│
├── producer/
│   └── topic_watcher.py                 ← Old method (still works but not recommended)
│
├── terminal2_kafka_with_manager.sh      ← NEW! Starts broker + topic manager
├── terminal2_kafka.sh                   ← Old: Only starts Kafka
│
└── config.json                          ← Configuration file
```

---

## 🔍 Detailed Breakdown

### 1️⃣ Topic Creation via Admin API

**Location**: `/broker/topic_manager.py` - Lines 62-95

```python
def create_kafka_topic(self, topic_name):
    """Create a topic in Kafka via Admin API"""
    
    # Create topic configuration
    topic = NewTopic(
        name=topic_name,
        num_partitions=self.config.get('default_partitions', 3),
        replication_factor=self.config.get('default_replication_factor', 1)
    )
    
    # Call Kafka Admin API
    self.admin_client.create_topics(new_topics=[topic], validate_only=False)
    
    # Update database status to 'active'
    update_topic_status(topic_name, 'active')
```

**Called by**: `process_approved_topics()` at line 164

---

### 2️⃣ Topic Deletion/Deactivation via Admin API

**Location**: `/broker/topic_manager.py` - Lines 97-121

```python
def delete_kafka_topic(self, topic_name):
    """Delete a topic from Kafka via Admin API"""
    
    # Call Kafka Admin API
    self.admin_client.delete_topics(topics=[topic_name])
    
    # Update database status to 'deleted'
    update_topic_status(topic_name, 'deleted')
```

**Called by**: `process_inactive_topics()` at line 181

---

### 3️⃣ Admin API Connection

**Location**: `/broker/topic_manager.py` - Lines 47-57

```python
def connect_admin_client(self):
    """Connect to Kafka Admin Client"""
    self.admin_client = KafkaAdminClient(
        bootstrap_servers=self.config['bootstrap_servers'],
        client_id=f'broker_topic_manager_{self.broker_id}'
    )
```

---

## 🚀 How to Run It

### Option 1: Integrated Script (Recommended)
```bash
./terminal2_kafka_with_manager.sh
```
This starts:
- Kafka Broker (background)
- Topic Manager Service (foreground) ← Handles all Admin API calls

### Option 2: Manually
```bash
# Terminal 1: Start Kafka
./terminal2_kafka.sh

# Terminal 2: Start Topic Manager
python3 broker/topic_manager.py
```

### Option 3: Run Once (Testing)
```bash
python3 broker/topic_manager.py --once
```

---

## 🎛️ Admin Interface for Deactivation

**Location**: `/admin/admin_panel.py` - Lines 121-157

```python
def deactivate_topics(self):
    """Deactivate active topics (mark for deletion)"""
    # Shows active topics
    # User selects topics to deactivate
    # Updates status to 'inactive'
    # Broker Topic Manager will delete them
```

**Access**:
```bash
python3 admin/admin_panel.py
# Choose option 4: Deactivate Topics
```

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOPIC LIFECYCLE VIA ADMIN API                │
└─────────────────────────────────────────────────────────────────┘

📝 CREATE FLOW:
┌──────────┐    ┌───────┐    ┌───────────────────────┐    ┌──────┐
│ Producer │───→│  DB   │───→│ broker/topic_manager  │───→│Kafka │
│ Requests │    │pending│    │ .create_kafka_topic() │    │Broker│
└──────────┘    └───────┘    │  (Admin API Call)     │    └──────┘
                              └───────────────────────┘
                                        ↓
                              ┌───────────────────┐
                              │  Update DB:       │
                              │  status='active'  │
                              └───────────────────┘

🗑️ DELETE FLOW:
┌──────────┐    ┌─────────┐    ┌───────────────────────┐    ┌──────┐
│  Admin   │───→│   DB    │───→│ broker/topic_manager  │───→│Kafka │
│  Panel   │    │inactive │    │ .delete_kafka_topic() │    │Broker│
└──────────┘    └─────────┘    │  (Admin API Call)     │    └──────┘
                                └───────────────────────┘
                                        ↓
                                ┌───────────────────┐
                                │  Update DB:       │
                                │  status='deleted' │
                                └───────────────────┘
```

---

## 🔧 Configuration

**Location**: `/config.json`

Key settings for Topic Manager:
```json
{
  "bootstrap_servers": "localhost:9092",         ← Kafka broker address
  "topic_manager_poll_interval": 5,              ← Check DB every 5 seconds
  "default_partitions": 3,                       ← New topic partitions
  "default_replication_factor": 1,               ← Replication factor
  "broker_id": 0                                 ← Broker identifier
}
```

---

## 🧪 Quick Test

```bash
# 1. Start the broker with topic manager
./terminal2_kafka_with_manager.sh

# 2. In another terminal, create an approved topic
sqlite3 topics.db "INSERT INTO topics (name, status) VALUES ('my-test', 'approved');"

# 3. Watch terminal 2 - you'll see:
# 📋 Topic Manager: Found 1 approved topic(s)
# 🔨 Topic Manager: Creating 'my-test'...
# ✓ Topic Manager: Created Kafka topic 'my-test'
#   ├─ Partitions: 3
#   └─ Replication Factor: 1
# ✅ Topic Manager: 'my-test' is now ACTIVE

# 4. Mark it for deletion
sqlite3 topics.db "UPDATE topics SET status='inactive' WHERE name='my-test';"

# 5. Watch terminal 2 again:
# 🗑️ Topic Manager: Found 1 inactive topic(s)
# 🔨 Topic Manager: Deleting 'my-test'...
# ✓ Topic Manager: Deleted Kafka topic 'my-test'
# ✅ Topic Manager: 'my-test' is now DELETED
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `broker/README.md` | Detailed Topic Manager documentation |
| `BROKER_TOPIC_MANAGEMENT.md` | Implementation summary |
| `BROKER_LOCATION.md` | This file - Quick reference |

---

## ✅ Summary

**Q: Where is topic creation/deactivation via Admin API?**

**A: `/broker/topic_manager.py`**

- **Creation**: Line 62-95 (`create_kafka_topic()`)
- **Deletion**: Line 97-121 (`delete_kafka_topic()`)
- **Connection**: Line 47-57 (`connect_admin_client()`)
- **Main Loop**: Line 232-253 (`run_loop()`)

**Run it with**: `./terminal2_kafka_with_manager.sh`

---

**Last Updated**: November 7, 2025
