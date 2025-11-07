# Troubleshooting: Producer Messages Not Reaching Consumer

## Common Issues and Solutions

### Issue 1: auto_offset_reset = "latest"
**Problem**: Consumer with `auto_offset_reset: "latest"` only reads NEW messages sent AFTER the consumer subscribes to the topic.

**Solution**: Change to `"earliest"` to read all messages from the beginning.

**Fix in config.json:**
```json
"auto_offset_reset": "earliest"
```

### Issue 2: Consumer Not Subscribed
**Problem**: Consumer must subscribe to a topic BEFORE it can receive messages.

**Check**:
1. In consumer, run: `subscribed`
2. Verify the topic you're sending to is in the list
3. If not, subscribe: `subscribe <topic_name>`

### Issue 3: Topic Not Active
**Problem**: Consumer can only subscribe to "active" topics.

**Check**:
1. In admin panel or web UI, verify topic status is "active"
2. If "pending", approve it in admin panel
3. Wait for topic_manager to create it in Kafka (check broker logs)

### Issue 4: Different Kafka Broker IPs
**Problem**: Producer and Consumer connecting to different Kafka brokers.

**Check all config.json files**:
- Producer system: `bootstrap_servers` should point to Kafka broker IP
- Consumer system: `bootstrap_servers` should point to SAME Kafka broker IP
- Current config shows: `192.168.191.169:9092`
- Verify this is correct for ALL systems

### Issue 5: Consumer Group Offset
**Problem**: Consumer group already has offset committed beyond current messages.

**Solution**: Reset consumer group offsets or use a new consumer group.

```bash
# On Kafka broker system
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group consumer_group_1 \
  --topic <topic_name> \
  --reset-offsets --to-earliest --execute
```

## Quick Diagnostic Steps

### Step 1: Verify Kafka Broker Connection
On each system (Producer, Consumer), test:
```bash
# Check if Kafka is reachable
telnet <kafka_broker_ip> 9092

# Example
telnet 192.168.191.169 9092
```

### Step 2: Check Topic Exists in Kafka
On Kafka broker system:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### Step 3: Verify Messages in Topic
On Kafka broker system:
```bash
# Read messages from beginning
kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic <topic_name> \
  --from-beginning
```

### Step 4: Check Producer Success
Producer should show:
```
✓ Publisher: Sent to '<topic>' [partition X, offset Y]
```

If you see this, message is in Kafka.

### Step 5: Check Consumer Subscription
Consumer should show:
```
📋 Active subscriptions: <topic1>, <topic2>
```

### Step 6: Test with Console Consumer
Bypass your application and test with Kafka's console consumer:
```bash
# On any system that can reach Kafka broker
kafka-console-consumer.sh --bootstrap-server 192.168.191.169:9092 \
  --topic <topic_name> \
  --from-beginning \
  --group test_group
```

## Recommended Fix Order

### Fix 1: Change auto_offset_reset to "earliest"
Edit config.json on ALL systems:
```json
"auto_offset_reset": "earliest"
```

### Fix 2: Restart Consumer
```bash
# Stop consumer (Ctrl+C)
# Start consumer again
python3 consumer/consumer.py
```

### Fix 3: Subscribe to Topic AFTER Restarting
```
subscribe <topic_name>
```

### Fix 4: Send Test Message
From producer:
```
send <topic_name> test message 123
```

### Fix 5: Verify Receipt
Consumer should display:
```
📨 [<topic_name>] test message 123
```

## If Still Not Working

### Check Database
```sql
-- Check topic status
SELECT * FROM topics WHERE name='<topic_name>';

-- Check user subscriptions
SELECT * FROM user_subscriptions WHERE user_id=1;
```

### Check Kafka Topic Details
```bash
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic <topic_name>
```

### Check Consumer Group Status
```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group consumer_group_1 --describe
```

## Network Architecture Checklist

Based on your distributed setup:
- **Admin/MySQL**: 192.168.191.183
- **Kafka Broker**: 192.168.191.169 (or 192.168.191.212?)
- **Producer**: 192.168.191.169
- **Consumer**: Different system

**CRITICAL**: Verify which system is running Kafka broker!

All systems must have:
```json
"bootstrap_servers": "<kafka_broker_ip>:9092"
```

## Common Mistake
**Sending message BEFORE consumer subscribes** with `auto_offset_reset: "latest"`:

1. Producer sends message → Message stored in Kafka
2. Consumer subscribes → Consumer offset set to END of log
3. Consumer reads → Nothing (message is BEFORE offset)

**Solution**: Either:
- Change to `"earliest"` to read all messages
- OR ensure consumer subscribes BEFORE producer sends messages
- OR reset consumer group offsets
