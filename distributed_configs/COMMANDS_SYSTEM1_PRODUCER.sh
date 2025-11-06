#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  SYSTEM 1: PRODUCER - TERMINAL COMMANDS
# ═══════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════"
echo "  SYSTEM 1: PRODUCER SETUP COMMANDS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Copy and paste these commands in order:"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 1: CONFIGURE IP ADDRESSES
# ═══════════════════════════════════════════════════════════════
cat << 'EOF'

# ──────────────────────────────────────────────────────────────
# STEP 1: Get Your System's IP Address
# ──────────────────────────────────────────────────────────────
hostname -I | awk '{print $1}'

# ✏️ WRITE DOWN:
# System 1 (This System) IP: ________________
# System 2 (Kafka Broker) IP: ________________
# System 4 (Admin/DB) IP: ________________
# System 4 Username: ________________


# ──────────────────────────────────────────────────────────────
# STEP 2: Clone Repository
# ──────────────────────────────────────────────────────────────
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream


# ──────────────────────────────────────────────────────────────
# STEP 3: Edit Setup Script with Your IP Addresses
# ──────────────────────────────────────────────────────────────
nano distributed_configs/setup_system1_producer.sh

# ✏️ EDIT THESE LINES (around line 10-13):
# SYSTEM2_IP="192.168.1.20"      ← Change to System 2 IP
# SYSTEM4_IP="192.168.1.40"      ← Change to System 4 IP
# SYSTEM4_USER="your_username"   ← Change to System 4 username

# Press: Ctrl+O (save), Enter, Ctrl+X (exit)


# ──────────────────────────────────────────────────────────────
# STEP 4: Run Setup Script
# ──────────────────────────────────────────────────────────────
cd distributed_configs
chmod +x setup_system1_producer.sh
./setup_system1_producer.sh

# ⏳ Wait for setup to complete...
# ✅ Setup will:
#    - Install Python dependencies
#    - Mount shared database from System 4
#    - Create config.json
#    - Test connectivity


# ──────────────────────────────────────────────────────────────
# STEP 5: Verify Setup
# ──────────────────────────────────────────────────────────────
# Test Kafka connectivity
telnet SYSTEM2_IP 9092
# Press Ctrl+] then type 'quit' to exit

# Test database mount
ls -la /mnt/shared_db/

# If database mount fails, manually mount:
# sudo mount SYSTEM4_IP:/home/SYSTEM4_USER/shared_db /mnt/shared_db


# ──────────────────────────────────────────────────────────────
# STEP 6: Start Producer
# ──────────────────────────────────────────────────────────────
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd producer
python3 producer.py

# ──────────────────────────────────────────────────────────────
# PRODUCER COMMANDS (Once Running):
# ──────────────────────────────────────────────────────────────
# create <topic_name>        - Create new topic (pending approval)
# send <topic_name> <msg>    - Send message to active topic
# list                       - List all topics
# active                     - List active topics
# help                       - Show help
# quit                       - Exit


# ──────────────────────────────────────────────────────────────
# TESTING:
# ──────────────────────────────────────────────────────────────
# 1. Create a topic:
#    > create news_updates
#
# 2. Go to System 4 (Admin) and approve it
#
# 3. Come back and send a message:
#    > send news_updates Hello from distributed system!

EOF
