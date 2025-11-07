# Admin Approve/Reject Topics - UI Guide

## ✅ Feature Already Implemented!

The web UI already has **full approve/reject functionality** for topics. Here's how to use it:

## Access the Web UI

1. **Open your browser** and go to:
   - Local: http://localhost:8080
   - Network: http://192.168.191.183:8080

2. **Click on the "👨‍💼 Admin Panel" tab** (first tab, should be active by default)

## How the Approve/Reject Feature Works

### Admin Panel View

The Admin Panel has two sections:

#### 1. **Pending Topic Approvals**
Shows all topics with status = "pending" that need admin approval.

Each pending topic displays:
- Topic name
- Creation timestamp
- Two action buttons:
  - **✓ Approve** (green button)
  - **✗ Reject** (red button)

#### 2. **All Topics**
Shows all topics regardless of status with color-coded badges:
- 🟢 **Active** - Topic is approved and running
- 🟡 **Pending** - Waiting for approval
- 🔴 **Rejected** - Admin rejected the topic
- ⚫ **Deactivated** - Topic was deactivated

Active topics have a **Deactivate** button to disable them.

## Step-by-Step: Approve a Topic

### Step 1: Producer Creates Topic Request
On the **📤 Producer** tab:
1. Enter producer ID (e.g., 1)
2. Enter topic name (e.g., "news-feed")
3. Click **"Create Topic Request"**
4. Topic is created with status = "pending"

### Step 2: Admin Sees Pending Request
On the **👨‍💼 Admin Panel** tab:
1. The new topic appears in "Pending Topic Approvals" section
2. You'll see:
   ```
   [Topic Name]
   Created: [timestamp]
   [✓ Approve] [✗ Reject]
   ```

### Step 3: Admin Approves Topic
1. Click the **✓ Approve** button
2. Alert shows: "Topic [name] approved successfully!"
3. Topic moves from "Pending" to "All Topics" with status = "active"
4. Topic disappears from "Pending Topic Approvals" section

### Step 4: Broker Creates Kafka Topic
The **Topic Manager** (running on broker) detects the status change:
1. Polls database every 5 seconds
2. Finds topic with status = "active"
3. Creates the actual Kafka topic
4. Updates database

### Step 5: Producer Can Now Send Messages
On the **📤 Producer** tab:
1. Topic now appears in "Select Topic" dropdown
2. Producer can send messages to the approved topic

## Step-by-Step: Reject a Topic

### Admin Rejects Topic
1. On **👨‍💼 Admin Panel** tab
2. Find the topic in "Pending Topic Approvals"
3. Click the **✗ Reject** button
4. Alert shows: "Topic [name] rejected!"
5. Topic status changes to "rejected"
6. Topic appears in "All Topics" with red "rejected" badge
7. Topic is NOT created in Kafka
8. Producer cannot send messages to it

## Workflow Diagram

```
Producer Creates Topic Request
        ↓
   status = "pending"
        ↓
   Appears in Admin Panel
   "Pending Topic Approvals"
        ↓
    ┌───┴───┐
    ↓       ↓
Approve   Reject
    ↓       ↓
 active   rejected
    ↓       
Topic Manager (Broker)
Creates Kafka Topic
    ↓
Producer Can Send Messages
```

## API Endpoints Used

### Approve Topic
```
POST /api/admin/approve
Body: {"topic_name": "topic-name"}
Response: {"success": true, "message": "Topic approved successfully!"}
```

### Reject Topic
```
POST /api/admin/reject
Body: {"topic_name": "topic-name"}
Response: {"success": true, "message": "Topic rejected!"}
```

### Deactivate Topic
```
POST /api/admin/deactivate
Body: {"topic_name": "topic-name"}
Response: {"success": true, "message": "Topic deactivated!"}
```

## Database Changes

### Approve
```sql
UPDATE topics SET status = 'active' WHERE name = 'topic-name';
```

### Reject
```sql
UPDATE topics SET status = 'rejected' WHERE name = 'topic-name';
```

### Deactivate
```sql
UPDATE topics SET status = 'deactivated' WHERE name = 'topic-name';
```

## Testing the Feature

### Test 1: Complete Approve Flow
```bash
# On Producer system
python3 producer/producer.py
> create test-topic-1

# On Admin UI (web browser)
1. Go to http://192.168.191.183:8080
2. Click "Admin Panel" tab
3. See "test-topic-1" in pending list
4. Click "✓ Approve"
5. See success message
6. Topic moves to "All Topics" as "active"

# On Broker system
# Topic Manager creates the Kafka topic automatically

# On Producer system
> send test-topic-1 "Hello World"
# Message sent successfully!
```

### Test 2: Reject Flow
```bash
# On Producer system
python3 producer/producer.py
> create spam-topic

# On Admin UI
1. Go to Admin Panel tab
2. See "spam-topic" in pending list
3. Click "✗ Reject"
4. See rejection message
5. Topic appears in "All Topics" as "rejected"

# On Producer system
> send spam-topic "test"
# Should fail - topic not active
```

## Troubleshooting

### Problem: Pending topics don't appear
**Solution**: 
- Check MySQL connection: `mysql -u kafka_user -pkafka_password -e "SELECT * FROM kafka_stream.topics;"`
- Verify web UI is connected to correct MySQL server (192.168.191.183)
- Check browser console for errors (F12)

### Problem: Approve button doesn't work
**Solution**:
- Check browser console (F12) for JavaScript errors
- Verify API endpoint is accessible: `curl -X POST http://localhost:8080/api/admin/approve -H "Content-Type: application/json" -d '{"topic_name":"test"}'`
- Check Flask logs in terminal where web UI is running

### Problem: Topic approved but not in Kafka
**Solution**:
- Check if Topic Manager is running on broker: `ps aux | grep topic_manager`
- Check Topic Manager logs for errors
- Verify Kafka broker is running: `kafka-topics.sh --bootstrap-server localhost:9092 --list`

## Real-Time Updates

The UI **auto-refreshes** every 5 seconds:
- Pending topics list updates automatically
- All topics list updates automatically
- No need to manually refresh the page

## Multiple Admins

Multiple admins can use the UI simultaneously:
- Each admin sees the same pending topics
- First admin to approve/reject wins
- Other admins see the updated status on next refresh

## Current Status

✅ **Fully Implemented Features:**
- View pending topics
- Approve topics (button click)
- Reject topics (button click)
- Deactivate active topics
- Real-time UI updates
- Status badges (pending/active/rejected/deactivated)
- Success/error alerts

✅ **Backend Functions:**
- `update_topic_status()` in db_setup.py
- `/api/admin/approve` endpoint
- `/api/admin/reject` endpoint
- `/api/admin/deactivate` endpoint

✅ **Frontend Features:**
- JavaScript functions: `approveTopic()`, `rejectTopic()`, `deactivateTopic()`
- Auto-refresh pending topics list
- Color-coded status badges
- Responsive design

## Summary

**You already have a fully functional approve/reject system!** 

Just:
1. Open http://localhost:8080 or http://192.168.191.183:8080
2. Go to Admin Panel tab
3. Click approve/reject buttons on pending topics

No code changes needed - everything is already implemented and working! 🎉
