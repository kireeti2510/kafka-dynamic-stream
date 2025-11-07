#!/bin/bash

# =============================================================================
# TERMINAL 2 - Kafka Broker with Topic Manager
# =============================================================================
# This terminal runs:
# 1. Kafka Broker service
# 2. Topic Manager service (manages topic lifecycle via Admin API)
#
# Start this AFTER ZooKeeper is fully running (wait 10-15 seconds)
# Keep this terminal running while using the application
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║          TERMINAL 2 - KAFKA BROKER + TOPIC MANAGER                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⏳ Make sure ZooKeeper (Terminal 1) is running first!"
echo ""
read -p "Press ENTER when ZooKeeper is ready..." 
echo ""

# =============================================================================
# Step 1: Start Kafka Broker
# =============================================================================
echo "Starting Kafka Broker..."
echo ""

# Check if Kafka is installed
if [ ! -d "/opt/kafka" ]; then
    echo "✗ Error: Kafka not found at /opt/kafka"
    echo "Please install Kafka first using SETUP_ENVIRONMENT.sh"
    exit 1
fi

# Start Kafka broker in background
cd /opt/kafka
nohup bin/kafka-server-start.sh config/server.properties > kafka-broker.log 2>&1 &
KAFKA_PID=$!

echo "✓ Kafka Broker started (PID: $KAFKA_PID)"
echo "  Log file: /opt/kafka/kafka-broker.log"
echo ""

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka broker to be ready (15 seconds)..."
sleep 15

# Verify Kafka is running
if ps -p $KAFKA_PID > /dev/null; then
    echo "✓ Kafka Broker is running"
else
    echo "✗ Kafka Broker failed to start. Check kafka-broker.log"
    exit 1
fi

echo ""

# =============================================================================
# Step 2: Activate Python environment and start Topic Manager
# =============================================================================
echo "Starting Topic Manager Service..."
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
    echo "✓ Virtual environment activated"
elif [ -d "$PROJECT_DIR/.venv" ]; then
    source "$PROJECT_DIR/.venv/bin/activate"
    echo "✓ Virtual environment activated"
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

echo ""

# Start Topic Manager (this will run in foreground)
cd "$PROJECT_DIR"
python3 broker/topic_manager.py

# When Topic Manager stops, also stop Kafka
echo ""
echo "Stopping Kafka Broker..."
if ps -p $KAFKA_PID > /dev/null; then
    kill $KAFKA_PID
    echo "✓ Kafka Broker stopped"
fi

echo ""
echo "👋 Broker services stopped"
