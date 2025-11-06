#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  SYSTEM 2: KAFKA BROKER - TERMINAL COMMANDS
# ═══════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════"
echo "  SYSTEM 2: KAFKA BROKER SETUP COMMANDS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Copy and paste these commands in order:"
echo ""

cat << 'EOF'

# ──────────────────────────────────────────────────────────────
# STEP 1: Get Your System's IP Address
# ──────────────────────────────────────────────────────────────
hostname -I | awk '{print $1}'

# ✏️ WRITE DOWN:
# System 2 (This System) IP: ________________


# ──────────────────────────────────────────────────────────────
# STEP 2: Clone Repository
# ──────────────────────────────────────────────────────────────
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream


# ──────────────────────────────────────────────────────────────
# STEP 3: Edit Setup Script with Your IP Address
# ──────────────────────────────────────────────────────────────
nano distributed_configs/setup_system2_kafka.sh

# ✏️ EDIT THIS LINE (around line 10):
# SYSTEM2_IP="192.168.1.20"      ← Change to YOUR System 2 IP

# Press: Ctrl+O (save), Enter, Ctrl+X (exit)


# ──────────────────────────────────────────────────────────────
# STEP 4: Run Setup Script
# ──────────────────────────────────────────────────────────────
cd distributed_configs
chmod +x setup_system2_kafka.sh
./setup_system2_kafka.sh

# ⏳ This will:
#    - Install Java
#    - Download and install Kafka
#    - Configure for network access
#    - Set up firewall
#    - Create systemd services
#    - Start Kafka and ZooKeeper
# 
# ⏰ Takes 5-10 minutes depending on download speed


# ──────────────────────────────────────────────────────────────
# STEP 5: Verify Kafka is Running
# ──────────────────────────────────────────────────────────────
# Check services
sudo systemctl status zookeeper
sudo systemctl status kafka

# List topics (should be empty initially)
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Check if Kafka port is open
sudo netstat -tlnp | grep 9092


# ──────────────────────────────────────────────────────────────
# STEP 6: Test from Other Systems
# ──────────────────────────────────────────────────────────────
# From System 1 or System 3, test connectivity:
# telnet SYSTEM2_IP 9092


# ══════════════════════════════════════════════════════════════
# KAFKA MANAGEMENT COMMANDS (For Later Use)
# ══════════════════════════════════════════════════════════════

# Start services (if not already running):
sudo systemctl start zookeeper
sudo systemctl start kafka

# Stop services:
sudo systemctl stop kafka
sudo systemctl stop zookeeper

# Restart services:
sudo systemctl restart kafka
sudo systemctl restart zookeeper

# View logs:
sudo journalctl -u kafka -f          # Kafka logs (real-time)
sudo journalctl -u zookeeper -f      # ZooKeeper logs (real-time)

# List topics:
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe a topic:
/opt/kafka/bin/kafka-topics.sh --describe --topic TOPIC_NAME --bootstrap-server localhost:9092

# Delete a topic:
/opt/kafka/bin/kafka-topics.sh --delete --topic TOPIC_NAME --bootstrap-server localhost:9092

# Check broker status:
/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# Monitor consumer groups:
/opt/kafka/bin/kafka-consumer-groups.sh --list --bootstrap-server localhost:9092


# ══════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ══════════════════════════════════════════════════════════════

# If Kafka won't start:
sudo journalctl -u kafka -n 50      # Check last 50 log lines

# If port 9092 is already in use:
sudo netstat -tlnp | grep 9092
sudo kill -9 <PID>

# Check firewall:
sudo ufw status
sudo ufw allow 9092/tcp
sudo ufw allow 2181/tcp

# Clean Kafka logs (if needed):
sudo rm -rf /tmp/kafka-logs/*
sudo rm -rf /tmp/zookeeper/*
# Then restart services

EOF
