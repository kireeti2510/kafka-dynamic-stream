#!/bin/bash

# =============================================================================
# TERMINAL 5 - Consumer
# =============================================================================
# This terminal runs the Consumer (User 1)
# The consumer subscribes to topics and receives messages
# You can run multiple consumers with different user IDs
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    TERMINAL 5 - CONSUMER (User 1)                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⏳ Make sure Kafka Broker (Terminal 2) is running first!"
echo ""
read -p "Press ENTER when Kafka is ready..." 
echo ""

# Navigate to project directory
cd /home/pes1ug23cs307/kafka_dynamic_stream

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run Consumer with User ID 1
# To run additional consumers, use different user IDs: python3 consumer/consumer.py 2
echo ""
echo "Starting Consumer (User ID: 1)..."
echo ""
python3 consumer/consumer.py 1

# When you exit, deactivate venv
deactivate
