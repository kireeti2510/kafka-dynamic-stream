# 🔄 Migration Guide: Producer-Side to Broker-Side Topic Management

## Overview

This guide explains how to migrate from the old producer-side topic management to the new broker-side topic management.

---

## What Changed?

### Before (Producer-Side)
- **Topic Watcher** ran as part of the Producer (3 threads)
- Producer managed topic creation via Admin API
- Topics created when Producer was running

### After (Broker-Side) ✅
- **Topic Manager** runs on Kafka Broker system
- Broker manages topic lifecycle via Admin API
- Topics managed independently of producer
- Support for topic deletion/deactivation

---

## Migration Steps

### Step 1: Update Configuration

Edit `config.json` to add new parameters:

```json
{
  "bootstrap_servers": "localhost:9092",
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_manager_poll_interval": 5,
  "sync_orphaned_topics": false,
  "broker_id": 0
}
```

### Step 2: Update Database Schema

The database schema now supports additional statuses. Run the database setup:

```bash
python3 admin/db_setup.py
```

This will automatically update the schema to support:
- `pending` - Topic requested
- `approved` - Approved by admin
- `active` - Created in Kafka ✅
- `inactive` - Marked for deletion ⚠️
- `deleted` - Removed from Kafka 🗑️

### Step 3: Use New Broker Startup Script

**Old Method:**
```bash
# Terminal 2
./terminal2_kafka.sh
```

**New Method (Recommended):**
```bash
# Terminal 2
./terminal2_kafka_with_manager.sh
```

This starts both:
1. Kafka Broker
2. Topic Manager Service

### Step 4: Update Admin Panel Usage

The Admin Panel now has an additional option:

**Before:**
```
1. View Pending Topics
2. Approve Topics
3. Reject Topics
4. View All Topics
5. View User Subscriptions
6. Exit
```

**After:**
```
1. View Pending Topics
2. Approve Topics
3. Reject Topics
4. Deactivate Topics (mark for deletion)  ← NEW!
5. View All Topics
6. View User Subscriptions
7. Exit
```

### Step 5: Update Producer (Optional)

The producer now runs in standard mode by default (no Topic Watcher).

If you want to use legacy mode:
```python
# In producer.py main()
coordinator = ProducerCoordinator(use_topic_watcher=True)
```

**Recommended:** Use default mode and let Broker manage topics.

---

## Backward Compatibility

### Legacy Mode Still Works

If you prefer the old method, you can still use it:

1. **Keep using** `./terminal2_kafka.sh` (broker only)
2. **Enable Topic Watcher** in producer:
   ```python
   coordinator = ProducerCoordinator(use_topic_watcher=True)
   ```

### Why Migrate?

Benefits of broker-side management:
- ✅ Better separation of concerns
- ✅ Topic deletion support
- ✅ Works with multiple producers
- ✅ Centralized control
- ✅ More scalable architecture

---

## Testing After Migration

### Test 1: Topic Creation

```bash
# 1. Start broker with manager
./terminal2_kafka_with_manager.sh

# 2. Start producer
./terminal4_producer.sh

# 3. Create topic
> create test_topic

# 4. Start admin panel and approve
python3 admin/admin_panel.py
Choice: 2
Enter: test_topic

# 5. Check broker terminal - should see:
✓ Topic Manager: Created Kafka topic 'test_topic'
✅ Topic Manager: 'test_topic' is now ACTIVE
```

### Test 2: Topic Deletion

```bash
# 1. In admin panel
Choice: 4
Enter: test_topic

# 2. Check broker terminal - should see:
✓ Topic Manager: Deleted Kafka topic 'test_topic'
✅ Topic Manager: 'test_topic' is now DELETED
```

---

## Troubleshooting

### Producer shows "Topic Watcher" messages

**Issue:** Producer still using legacy mode

**Solution:** 
- Make sure you're using updated `producer.py`
- Check that `use_topic_watcher=False` (default)

### Topics not being created

**Issue:** Broker Topic Manager not running

**Solution:**
- Use `./terminal2_kafka_with_manager.sh`
- Or manually run: `python3 broker/topic_manager.py`

### Database errors with new statuses

**Issue:** Old database schema

**Solution:**
```bash
# Backup old database
cp topics.db topics.db.backup

# Remove old database
rm topics.db

# Re-initialize with new schema
python3 admin/db_setup.py
```

### Want to keep old data

**Solution:** Manual migration:
```bash
# The new schema is backward compatible
# Just need to allow new statuses
sqlite3 topics.db

# Check current schema
.schema topics

# If needed, recreate table allowing new statuses
# (This will preserve data)
```

---

## Rollback Procedure

If you need to rollback to the old system:

1. **Stop broker services:**
   ```bash
   # Stop terminal2_kafka_with_manager.sh
   Ctrl+C
   ```

2. **Start old broker:**
   ```bash
   ./terminal2_kafka.sh
   ```

3. **Enable Topic Watcher in producer:**
   ```python
   coordinator = ProducerCoordinator(use_topic_watcher=True)
   ```

4. **Restore old database (if backed up):**
   ```bash
   cp topics.db.backup topics.db
   ```

---

## File Changes Summary

### New Files Created:
- `broker/topic_manager.py` - Main topic management service
- `broker/README.md` - Broker documentation
- `terminal2_kafka_with_manager.sh` - Integrated startup script
- `BROKER_TOPIC_MANAGEMENT.md` - Implementation guide
- `BROKER_LOCATION.md` - Quick reference
- `QUICK_ANSWER.md` - Ultra-quick reference
- `MIGRATION_GUIDE.md` - This file

### Modified Files:
- `admin/db_setup.py` - Added inactive/deleted statuses
- `admin/admin_panel.py` - Added deactivation option
- `producer/producer.py` - Made Topic Watcher optional
- `config.json` - Added broker config parameters
- `README.md` - Updated documentation
- `START_GUIDE.sh` - Updated startup instructions
- `QUICK_REFERENCE.sh` - Updated commands

### Unchanged Files:
- `producer/topic_watcher.py` - Still available for legacy mode
- `producer/input_listener.py` - No changes
- `consumer/consumer.py` - No changes
- `web/app.py` - No changes

---

## Support

For questions or issues:
1. Check `BROKER_LOCATION.md` for quick reference
2. See `broker/README.md` for detailed documentation
3. Review `BROKER_TOPIC_MANAGEMENT.md` for architecture

---

**Migration Date:** November 7, 2025  
**Status:** ✅ Complete and Ready
