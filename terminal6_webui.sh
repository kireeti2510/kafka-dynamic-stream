#!/bin/bash

# =============================================================================
# TERMINAL 6 - Web UI (Optional)
# =============================================================================
# This terminal runs the Flask web dashboard
# View real-time topics and subscriptions at http://localhost:5000
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    TERMINAL 6 - WEB UI                                ║"
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

# Run Web UI
echo ""
echo "Starting Web UI..."
echo "Open your browser to: http://localhost:5000"
echo ""
python3 web/app.py

# When you exit, deactivate venv
deactivate
