#!/bin/bash

# =============================================================================
# KAFKA DYNAMIC STREAM - COMPLETE STARTUP GUIDE
# =============================================================================
# This script provides step-by-step instructions to get the system running
# =============================================================================

cat << 'EOF'

╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║        🚀 KAFKA DYNAMIC STREAM - STARTUP GUIDE 🚀                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝


📋 PREREQUISITES CHECK
═══════════════════════════════════════════════════════════════════════

EOF

# Check Python
echo -n "Checking Python 3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✓ Found: Python $PYTHON_VERSION"
else
    echo "❌ Python 3 not found!"
    echo "   Install: sudo apt install python3"
    exit 1
fi

# Check Kafka
echo -n "Checking Kafka installation... "
if [ -d "/opt/kafka" ]; then
    echo "✓ Found: /opt/kafka"
else
    echo "❌ Kafka not found at /opt/kafka"
    echo "   Please install Kafka first!"
    exit 1
fi

# Check Java
echo -n "Checking Java... "
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo "✓ Found: $JAVA_VERSION"
else
    echo "❌ Java not found!"
    echo "   Install: sudo apt install default-jdk"
    exit 1
fi

cat << 'EOF'


═══════════════════════════════════════════════════════════════════════
STEP 1: INSTALL PYTHON DEPENDENCIES
═══════════════════════════════════════════════════════════════════════

EOF

echo "Installing required Python packages..."
echo ""
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Dependencies installed successfully!"
else
    echo ""
    echo "❌ Failed to install dependencies"
    echo "   Try: pip3 install --user -r requirements.txt"
    exit 1
fi

cat << 'EOF'


═══════════════════════════════════════════════════════════════════════
STEP 2: INITIALIZE DATABASE
═══════════════════════════════════════════════════════════════════════

EOF

echo "Initializing SQLite database..."
echo ""
python3 admin/db_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Database initialized successfully!"
else
    echo ""
    echo "❌ Failed to initialize database"
    exit 1
fi

cat << 'EOF'


═══════════════════════════════════════════════════════════════════════
STEP 3: START KAFKA SERVICES
═══════════════════════════════════════════════════════════════════════

Now you need to start Kafka services in separate terminals.

Open 2 NEW TERMINAL WINDOWS and run these commands:

EOF

echo "📌 TERMINAL 1 - Start ZooKeeper:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd /opt/kafka"
echo "bin/zookeeper-server-start.sh config/zookeeper.properties"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 TERMINAL 2 - Start Kafka Broker:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd /opt/kafka"
echo "bin/kafka-server-start.sh config/server.properties"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Wait about 10-15 seconds for services to fully start..."
echo ""

# Wait for user confirmation
read -p "Press ENTER once both Kafka services are running... " 

cat << 'EOF'


═══════════════════════════════════════════════════════════════════════
STEP 4: VERIFY KAFKA ENVIRONMENT
═══════════════════════════════════════════════════════════════════════

Running Kafka environment validation...

EOF

python3 kafka_env_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Kafka environment validated successfully!"
else
    echo ""
    echo "❌ Kafka validation failed!"
    echo "   Make sure ZooKeeper and Kafka Broker are running"
    exit 1
fi

cat << 'EOF'


═══════════════════════════════════════════════════════════════════════
✅ SETUP COMPLETE - READY TO START APPLICATION!
═══════════════════════════════════════════════════════════════════════

Now open 4 MORE TERMINALS and run these commands:

EOF

echo "📌 TERMINAL 3 - Admin Panel:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd $(pwd)"
echo "python3 admin/admin_panel.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 TERMINAL 4 - Producer:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd $(pwd)"
echo "python3 producer/producer.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 TERMINAL 5 - Consumer (User 1):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd $(pwd)"
echo "python3 consumer/consumer.py 1"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📌 TERMINAL 6 - Web UI (Optional):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "cd $(pwd)"
echo "python3 web/app.py"
echo "Then visit: http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat << 'EOF'


═══════════════════════════════════════════════════════════════════════
🎯 QUICK TEST WORKFLOW
═══════════════════════════════════════════════════════════════════════

1️⃣  In PRODUCER terminal:
   > create news_updates
   (Topic created with status: PENDING)

2️⃣  In ADMIN terminal:
   Choose option: 2 (Approve Topics)
   Enter: news_updates
   (Topic approved)

3️⃣  Wait 5 seconds (Topic Watcher creates it in Kafka)
   (You'll see: 'news_updates' is now ACTIVE)

4️⃣  In CONSUMER terminal:
   > subscribe news_updates
   (Subscribed to topic)

5️⃣  In PRODUCER terminal:
   > send news_updates Hello, this is a test message!
   (Message sent)

6️⃣  In CONSUMER terminal:
   (You should see the message received!)


═══════════════════════════════════════════════════════════════════════
📚 HELPFUL COMMANDS
═══════════════════════════════════════════════════════════════════════

Producer Commands:
  create <topic>              - Create new topic
  send <topic> <message>      - Send message
  list                        - List all topics
  active                      - List active topics
  help                        - Show help
  quit                        - Exit

Consumer Commands:
  list                        - List active topics
  subscribed                  - Show your subscriptions
  subscribe <topic1> ...      - Subscribe to topics
  unsubscribe <topic1> ...    - Unsubscribe
  refresh                     - Refresh subscriptions
  quit                        - Exit

Admin Commands:
  1 - View pending topics
  2 - Approve topics
  3 - Reject topics
  4 - View all topics
  5 - View subscriptions
  6 - Exit


═══════════════════════════════════════════════════════════════════════
🔧 TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════

Problem: "Connection refused"
Solution: Make sure ZooKeeper and Kafka are running in separate terminals

Problem: "Topic not created"
Solution: Check the approval flow: pending → approved → active

Problem: "No messages received"
Solution: Ensure topic is 'active' and consumer is subscribed

Problem: Services won't start
Solution: Check logs in /opt/kafka/logs/


═══════════════════════════════════════════════════════════════════════
📖 DOCUMENTATION
═══════════════════════════════════════════════════════════════════════

For detailed information, see:
  - README.md              - Complete project guide
  - QUICK_REFERENCE.sh     - All commands reference
  - KAFKA_ENV_SETUP.md     - Environment validation guide
  - ENHANCEMENT_SUMMARY.md - Latest features


═══════════════════════════════════════════════════════════════════════

🚀 You're all set! Start the terminals and begin streaming! 🚀

═══════════════════════════════════════════════════════════════════════

EOF
