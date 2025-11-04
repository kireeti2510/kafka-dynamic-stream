#!/bin/bash

# =============================================================================
# TERMINAL 3 - Admin Panel
# =============================================================================
# This terminal runs the Admin Panel for approving/rejecting topics
# Run this after Kafka Broker is fully started
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    TERMINAL 3 - ADMIN PANEL                           ║"
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

# Run Admin Panel
echo ""
echo "Starting Admin Panel..."
echo ""
python3 admin/admin_panel.py

# When you exit, deactivate venv
deactivate
