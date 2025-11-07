# ⚡ QUICK ANSWER: Where is Topic Creation/Deactivation via Admin API?

## 📍 Location: `/broker/topic_manager.py`

```
/Users/kireetireddyp/kafka-dynamic-stream/broker/topic_manager.py
```

---

## 🎯 Exact Line Numbers

### Admin API Connection
```python
Lines 47-57: connect_admin_client()
    ↓
    Creates KafkaAdminClient instance
    Connects to Kafka broker
```

### Topic Creation (via Admin API)
```python
Lines 62-95: create_kafka_topic()
    ↓
    Line 74: self.admin_client.create_topics(...)  ← ADMIN API CALL
    Creates topic in Kafka
    Updates DB status to 'active'
```

### Topic Deletion/Deactivation (via Admin API)
```python
Lines 97-121: delete_kafka_topic()
    ↓
    Line 112: self.admin_client.delete_topics(...)  ← ADMIN API CALL
    Deletes topic from Kafka
    Updates DB status to 'deleted'
```

### Main Processing Loop
```python
Lines 164-179: process_approved_topics()
    ↓
    Monitors DB for status='approved'
    Calls create_kafka_topic()

Lines 181-201: process_inactive_topics()
    ↓
    Monitors DB for status='inactive'
    Calls delete_kafka_topic()

Lines 232-253: run_loop()
    ↓
    Continuously runs every 5 seconds
```

---

## 🚀 How to Start

```bash
# Simple: Use the integrated script
./terminal2_kafka_with_manager.sh

# Or manually:
python3 broker/topic_manager.py
```

---

## 📊 Visual Map

```
broker/topic_manager.py
│
├─ Line 21: Import KafkaAdminClient, NewTopic
├─ Line 47: connect_admin_client() ──────┐
│                                          │
├─ Line 62: create_kafka_topic()          │
│   └─ Line 74: create_topics() ◄─────────┤ ADMIN API
│                                          │
├─ Line 97: delete_kafka_topic()          │
│   └─ Line 112: delete_topics() ◄────────┘
│
├─ Line 164: process_approved_topics()
│   └─ Calls create_kafka_topic()
│
├─ Line 181: process_inactive_topics()
│   └─ Calls delete_kafka_topic()
│
└─ Line 232: run_loop()
    └─ Orchestrates everything
```

---

## 🎛️ Admin Panel Integration

File: `/admin/admin_panel.py`

```
Line 121-157: deactivate_topics()
    ↓
    Marks topics as 'inactive' in DB
    Broker Topic Manager picks them up
    Deletes from Kafka automatically
```

---

## ✅ That's It!

**All topic creation/deactivation via Kafka Admin API** happens in:

`/broker/topic_manager.py`

**Start it with:**

`./terminal2_kafka_with_manager.sh`
