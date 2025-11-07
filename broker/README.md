# Kafka Broker - Topic Manager Service

This module manages the complete lifecycle of Kafka topics via the Kafka Admin API, running on the broker system.

## 🎯 Overview

The **Broker Topic Manager** is a service that runs alongside your Kafka broker and handles:
- ✅ **Topic Creation**: Monitors for approved topics → Creates them in Kafka → Marks as active
- ❌ **Topic Deletion**: Monitors for inactive topics → Deletes them from Kafka → Marks as deleted
- 🔄 **Status Synchronization**: Keeps database and Kafka cluster in sync

## 📊 Topic Lifecycle

```
┌─────────┐     ┌──────────┐     ┌────────┐     ┌──────────┐     ┌─────────┐
│ pending │ --> │ approved │ --> │ active │ --> │ inactive │ --> │ deleted │
└─────────┘     └──────────┘     └────────┘     └──────────┘     └─────────┘
     ^                |                |               |               |
     |           [BROKER]          [EXISTS]        [BROKER]        [REMOVED]
  [PRODUCER]      CREATES          IN KAFKA        DELETES        FROM KAFKA
   REQUESTS        TOPIC                            TOPIC
```

### Status Meanings:
- **pending**: Topic requested by producer, awaiting admin approval
- **approved**: Admin approved, waiting for broker to create in Kafka
- **active**: Topic exists in Kafka and is operational
- **inactive**: Admin marked for deletion, waiting for broker to remove
- **deleted**: Topic removed from Kafka (historical record)

## 🚀 Usage

### Start with Kafka Broker

Use the integrated startup script:

```bash
./terminal2_kafka_with_manager.sh
```

This starts both:
1. Kafka Broker (background)
2. Topic Manager Service (foreground)

### Standalone Mode

Start just the Topic Manager:

```bash
# With default config.json
python3 broker/topic_manager.py

# With custom config
python3 broker/topic_manager.py --config /path/to/config.json

# Run once and exit (no continuous loop)
python3 broker/topic_manager.py --once
```

## ⚙️ Configuration

Edit `config.json` to configure the Topic Manager:

```json
{
  "bootstrap_servers": "localhost:9092",
  "topic_manager_poll_interval": 5,
  "default_partitions": 3,
  "default_replication_factor": 1,
  "sync_orphaned_topics": false,
  "broker_id": 0
}
```

### Parameters:
- `topic_manager_poll_interval`: Seconds between database checks (default: 5)
- `default_partitions`: Number of partitions for new topics (default: 3)
- `default_replication_factor`: Replication factor for new topics (default: 1)
- `sync_orphaned_topics`: Check for orphaned topics in Kafka (default: false)
- `broker_id`: Identifier for this broker (default: 0)

## 📝 Features

### 1. Topic Creation
- Polls database every N seconds for topics with status `'approved'`
- Creates them in Kafka using Admin API
- Updates status to `'active'` in database
- Logs success/failure with details

### 2. Topic Deletion
- Polls database for topics with status `'inactive'`
- Deletes them from Kafka using Admin API
- Updates status to `'deleted'` in database
- Preserves historical records in database

### 3. Orphan Detection (Optional)
- Finds topics in Kafka that aren't marked as `'active'` in database
- Useful for cleanup and consistency checks
- Enable with `"sync_orphaned_topics": true`

## 🔧 Integration with Admin Panel

The Admin Panel now supports topic deactivation:

```bash
python3 admin/admin_panel.py
```

Menu Options:
1. View Pending Topics
2. Approve Topics
3. Reject Topics
4. **Deactivate Topics** ← NEW! Mark active topics for deletion
5. View All Topics (shows all statuses including inactive/deleted)
6. View User Subscriptions
7. Exit

## 🏗️ Architecture

### Old Design (Producer-side)
```
Producer → topic_watcher.py → Kafka Admin API → Kafka Broker
```

### New Design (Broker-side) ✅
```
Kafka Broker System:
├── Kafka Server (bin/kafka-server-start.sh)
└── Topic Manager (broker/topic_manager.py)
    ├── Monitors Database
    ├── Creates Topics → Kafka
    └── Deletes Topics → Kafka
```

## 📋 Example Workflow

### Creating a Topic

1. **Producer** requests topic:
   ```python
   # Producer creates topic request
   add_topic('my-new-topic', status='pending')
   ```

2. **Admin** approves:
   ```bash
   # In admin panel, approve the topic
   Choice: 2 (Approve Topics)
   >> my-new-topic
   ```

3. **Broker Topic Manager** creates:
   ```
   📋 Found 1 approved topic(s) to create
   🔨 Creating 'my-new-topic'...
   ✓ Created Kafka topic 'my-new-topic'
     ├─ Partitions: 3
     └─ Replication Factor: 1
   ✅ 'my-new-topic' is now ACTIVE
   ```

### Deleting a Topic

1. **Admin** deactivates:
   ```bash
   # In admin panel
   Choice: 4 (Deactivate Topics)
   >> my-new-topic
   ```

2. **Broker Topic Manager** deletes:
   ```
   🗑️  Found 1 inactive topic(s) to delete
   🔨 Deleting 'my-new-topic'...
   ✓ Deleted Kafka topic 'my-new-topic'
   ✅ 'my-new-topic' is now DELETED
   ```

## 🛠️ Troubleshooting

### Topic Manager won't connect
```
✗ Failed to connect to Kafka Admin API
```
**Solution**: Ensure Kafka broker is running first

### Topics not being created
```
✗ Failed to create topic in Kafka
```
**Checks**:
1. Verify `bootstrap_servers` in config.json
2. Check Kafka broker is running
3. Verify database has topics with status='approved'
4. Check Topic Manager logs for errors

### Manual Database Check
```bash
sqlite3 topics.db "SELECT name, status FROM topics;"
```

## 📄 Files

- `broker/topic_manager.py` - Main Topic Manager service
- `broker/README.md` - This documentation
- `terminal2_kafka_with_manager.sh` - Integrated startup script
- `admin/admin_panel.py` - Admin UI (updated with deactivation)
- `admin/db_setup.py` - Database schema (updated with new statuses)

## 🔄 Migration from Old System

If you were using `producer/topic_watcher.py`:

1. **Stop** the old topic watcher
2. **Update** database schema (automatic on next run)
3. **Use** new broker startup script: `./terminal2_kafka_with_manager.sh`
4. The Topic Manager replaces the old topic_watcher functionality

The old `topic_watcher.py` is **no longer needed** when using the broker-side Topic Manager.

## 📚 Related Documentation

- [Admin Panel Guide](../admin/README.md)
- [Database Setup](../admin/db_setup.py)
- [Configuration Guide](../README.md)
