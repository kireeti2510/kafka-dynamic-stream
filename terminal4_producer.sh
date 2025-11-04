#!/bin/bash

# =============================================================================
# TERMINAL 4 - Producer
# =============================================================================
# This terminal runs the multi-threaded Producer
# The producer handles topic creation and message publishing
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    TERMINAL 4 - PRODUCER                              ║"
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

# Run Producer
echo ""
echo "Starting Producer..."
echo ""
python3 producer/producer.py

# When you exit, deactivate venv
deactivate
