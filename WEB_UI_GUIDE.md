# 🌐 Interactive Web UI Guide

## Overview

The new interactive web UI provides a complete web-based interface for all Kafka Dynamic Stream operations while **retaining all existing terminal functionality**.

## Features

### 👨‍💼 Admin Panel (Web)
- View pending topic requests
- Approve topics with one click
- Reject topic requests
- Deactivate active topics
- View all topics with status indicators

### 📤 Producer Interface (Web)
- Create topic requests
- Send messages to active topics
- View your topic request statuses
- Real-time feedback

### 📥 Consumer Interface (Web)
- Subscribe to active topics
- Unsubscribe from topics
- View your subscriptions
- See received messages

### 📊 Dashboard
- System statistics
- Active topics overview
- All subscriptions view
- Auto-refresh every 5 seconds

## Quick Start

### 1. Start the Interactive Web UI

```bash
cd /Users/kireetireddyp/kafka-dynamic-stream
python3 web/interactive_app.py
```

### 2. Access the Web Interface

Open your browser to:
- **Local**: http://localhost:8080
- **Network**: http://192.168.191.183:8080

## Usage Examples

### Admin Operations

1. Go to the **Admin Panel** tab
2. View pending topics in the "Pending Topic Approvals" section
3. Click **✓ Approve** to approve a topic (Kafka will create it automatically)
4. Click **✗ Reject** to reject a topic request
5. In "All Topics" section, click **Deactivate** to mark an active topic for deletion

### Producer Operations

1. Go to the **Producer** tab
2. Enter your Producer ID (e.g., 1)
3. To create a topic:
   - Enter topic name
   - Click **Create Topic Request**
   - Wait for admin approval
4. To send messages:
   - Select an active topic from dropdown
   - Type your message
   - Click **Send Message**

### Consumer Operations

1. Go to the **Consumer** tab
2. Enter your Consumer ID (e.g., 1)
3. To subscribe:
   - Select a topic from dropdown
   - Click **Subscribe**
4. View your subscriptions in "My Subscriptions"
5. Click **×** on any subscription to unsubscribe
6. Messages appear in "Received Messages" section

## Terminal Commands Still Work!

All existing terminal commands continue to work alongside the web UI:

```bash
# Admin Panel (Terminal)
python3 admin/admin_panel.py

# Producer (Terminal)
python3 producer/producer.py

# Consumer (Terminal)
python3 consumer/consumer.py 1
```

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Browser                         │
│                  http://localhost:8080                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Interactive Web UI (Flask)                 │
│              web/interactive_app.py                     │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │Admin Panel  │  │  Producer   │  │  Consumer   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└────────────┬──────────────┬─────────────┬──────────────┘
             │              │             │
             ▼              ▼             ▼
    ┌────────────┐   ┌──────────┐  ┌──────────┐
    │   MySQL    │   │  Kafka   │  │  Kafka   │
    │  Database  │   │  Broker  │  │ Consumer │
    └────────────┘   └──────────┘  └──────────┘
```

## Available Endpoints

### Web Pages
- `GET /` - Main dashboard

### API Endpoints

#### Topics
- `GET /api/topics/all` - Get all topics
- `GET /api/topics/pending` - Get pending topics
- `GET /api/topics/active` - Get active topics
- `GET /api/stats` - Get system statistics

#### Admin
- `POST /api/admin/approve` - Approve topic
- `POST /api/admin/reject` - Reject topic
- `POST /api/admin/deactivate` - Deactivate topic

#### Producer
- `GET /api/producer/topics/<producer_id>` - Get producer's topics
- `POST /api/producer/create` - Create topic request
- `POST /api/producer/send` - Send message

#### Consumer
- `GET /api/consumer/subscriptions/<consumer_id>` - Get subscriptions
- `POST /api/consumer/subscribe` - Subscribe to topic
- `POST /api/consumer/unsubscribe` - Unsubscribe from topic
- `GET /api/consumer/messages/<consumer_id>` - Get messages

## Comparison: Web UI vs Terminal

| Feature | Web UI | Terminal |
|---------|--------|----------|
| Admin Approval | ✓ One-click | ✓ Interactive menu |
| Create Topics | ✓ Form-based | ✓ Command-based |
| Send Messages | ✓ Text area | ✓ Command line |
| Subscribe | ✓ Dropdown select | ✓ Command-based |
| View Status | ✓ Real-time dashboard | ✓ List commands |
| Auto-refresh | ✓ Every 5 seconds | ✗ Manual refresh |
| Multi-user | ✓ Multiple browsers | ✓ Multiple terminals |
| Accessibility | ✓ From any device | ✓ SSH/Terminal only |

## Running Both Interfaces

You can run both the web UI and terminal interfaces simultaneously:

**Terminal 1 - Web UI:**
```bash
python3 web/interactive_app.py
```

**Terminal 2 - Admin Panel:**
```bash
python3 admin/admin_panel.py
```

**Terminal 3 - Producer:**
```bash
python3 producer/producer.py
```

**Terminal 4 - Consumer:**
```bash
python3 consumer/consumer.py 1
```

Both interfaces share the same MySQL database and Kafka broker, so changes made in one are immediately visible in the other!

## Troubleshooting

### Port 8080 Already in Use
Edit `web/interactive_app.py` and change the port:
```python
app.run(host='0.0.0.0', port=8081, debug=False)
```

### Cannot Connect to MySQL
Check your `config.json` has correct MySQL settings:
```json
{
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "kafka_password"
  }
}
```

### Cannot Connect to Kafka
Ensure Kafka broker is running and `bootstrap_servers` in `config.json` is correct:
```json
{
  "bootstrap_servers": "192.168.191.212:9092"
}
```

### Messages Not Appearing
The web UI message viewing is for demonstration. For full real-time message consumption, use the terminal consumer which has proper Kafka consumer groups.

## Security Note

⚠️ This is a development interface. For production use, add:
- Authentication/Authorization
- HTTPS/SSL
- Input validation and sanitization
- Rate limiting
- CORS configuration
- Session management

## Next Steps

1. Start the web UI: `python3 web/interactive_app.py`
2. Open http://localhost:8080 in your browser
3. Create topics as Producer
4. Approve them as Admin
5. Subscribe as Consumer
6. Send and receive messages!

Enjoy the new interactive interface! 🚀
