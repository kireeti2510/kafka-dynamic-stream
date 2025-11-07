#!/bin/bash

# QUICK REFERENCE - Kafka Dynamic Stream
# Copy-paste commands for easy testing

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  KAFKA DYNAMIC STREAM - QUICK REFERENCE COMMANDS         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if in correct directory
if [ ! -f "config.json" ]; then
    echo "❌ Please run this from the kafka_dynamic_stream directory"
    exit 1
fi

cat << 'EOF'

═══════════════════════════════════════════════════════════════
 1️⃣  KAFKA INFRASTRUCTURE
═══════════════════════════════════════════════════════════════

# Terminal 1 - Start Zookeeper
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties

# Terminal 2 - Start Kafka Broker + Topic Manager (RECOMMENDED)
cd kafka-dynamic-stream
./terminal2_kafka_with_manager.sh

# OR (legacy - broker only, no topic management)
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties


═══════════════════════════════════════════════════════════════
 2️⃣  APPLICATION COMPONENTS
═══════════════════════════════════════════════════════════════

# Admin Panel (Terminal 3)
python3 admin/admin_panel.py

# Producer (Terminal 4)
python3 producer/producer.py

# Consumer User 1 (Terminal 5)
python3 consumer/consumer.py 1

# Consumer User 2 (Terminal 6)
python3 consumer/consumer.py 2

# Web UI (Terminal 7)
python3 web/app.py
# Then visit: http://localhost:5000


═══════════════════════════════════════════════════════════════
 3️⃣  PRODUCER COMMANDS (In producer terminal)
═══════════════════════════════════════════════════════════════

create news_updates
create weather_data
create stock_prices
create tech_news
create sports_updates

list
active

send news_updates Breaking: Major announcement today!
send weather_data Sunny, temperature 25°C
send stock_prices AAPL: $150.23, GOOGL: $2800.45

help
quit


═══════════════════════════════════════════════════════════════
 4️⃣  ADMIN PANEL COMMANDS (In admin terminal)
═══════════════════════════════════════════════════════════════

1  # View pending topics
2  # Approve topics (enter: all OR news_updates,weather_data)
3  # Reject topics
4  # Deactivate topics (mark for deletion from Kafka)
5  # View all topics
6  # View subscriptions
7  # Exit


═══════════════════════════════════════════════════════════════
 5️⃣  CONSUMER COMMANDS (In consumer terminal)
═══════════════════════════════════════════════════════════════

list
subscribed

subscribe news_updates weather_data
subscribe stock_prices tech_news

unsubscribe weather_data

refresh
help
quit


═══════════════════════════════════════════════════════════════
 6️⃣  KAFKA CLI TOOLS (Debugging)
═══════════════════════════════════════════════════════════════

# List all topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe a topic
/opt/kafka/bin/kafka-topics.sh --describe --topic news_updates --bootstrap-server localhost:9092

# List consumer groups
/opt/kafka/bin/kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# Delete a topic (if needed)
/opt/kafka/bin/kafka-topics.sh --delete --topic test_topic --bootstrap-server localhost:9092


═══════════════════════════════════════════════════════════════
 7️⃣  DATABASE QUERIES (Debugging)
═══════════════════════════════════════════════════════════════

sqlite3 topics.db "SELECT * FROM topics;"
sqlite3 topics.db "SELECT * FROM user_subscriptions;"
sqlite3 topics.db "SELECT name, status FROM topics ORDER BY created_at DESC;"


═══════════════════════════════════════════════════════════════
 8️⃣  COMPLETE WORKFLOW EXAMPLE
═══════════════════════════════════════════════════════════════

STEP 1 (Producer):
> create news_updates

STEP 2 (Admin):
Choice: 2
Enter topics: news_updates
(Or enter: all)

STEP 3 (Wait for Broker Topic Manager - automatic):
✓ Topic Manager: Created Kafka topic 'news_updates'
✓ Topic Manager: 'news_updates' is now ACTIVE

STEP 4 (Consumer):
> subscribe news_updates

STEP 5 (Producer):
> send news_updates This is breaking news!

STEP 6 (Consumer - receives):
📨 [news_updates] Message received:
   Content: This is breaking news!


═══════════════════════════════════════════════════════════════
 9️⃣  TESTING SCENARIOS
═══════════════════════════════════════════════════════════════

TEST 1: Basic Flow
- Create topic → Approve → Subscribe → Send → Receive ✓

TEST 2: Multiple Topics
- Create 3 topics → Approve all → Consumer subscribes to 2
- Send to all 3 → Consumer only receives from subscribed 2 ✓

TEST 3: Multiple Consumers
- Consumer 1 subscribes to A, B
- Consumer 2 subscribes to B, C
- Send to A, B, C → Each receives their subscriptions ✓

TEST 4: Dynamic Subscription
- Consumer running
- New topic created & activated
- Consumer subscribes without restart ✓


═══════════════════════════════════════════════════════════════
 🔟  TROUBLESHOOTING
═══════════════════════════════════════════════════════════════

Problem: Connection refused
Solution: Check Kafka is running
  ps aux | grep kafka

Problem: Topic not created
Solution: Check approval flow
  1. Producer created (pending)
  2. Admin approved (approved)
  3. Broker Topic Manager activated (active)

Problem: How to delete a topic?
Solution: Use Admin Panel option 4
  1. Start admin panel
  2. Choose 4 (Deactivate Topics)
  3. Enter topic name
  4. Broker will delete from Kafka

Problem: No messages received
Solution: 
  1. Check topic is 'active' not 'approved'
  2. Verify subscription: > subscribed
  3. Check producer sent to correct topic

Problem: Web UI empty
Solution: 
  python3 admin/db_setup.py
  (Re-initialize database)


═══════════════════════════════════════════════════════════════
 📚  API ENDPOINTS (Web UI)
═══════════════════════════════════════════════════════════════

http://localhost:5000/              # Dashboard
http://localhost:5000/topics        # All topics JSON
http://localhost:5000/active        # Active topics JSON
http://localhost:5000/subscriptions # Subscriptions JSON
http://localhost:5000/health        # Health check


═══════════════════════════════════════════════════════════════

For detailed documentation, see README.md

═══════════════════════════════════════════════════════════════

EOF
