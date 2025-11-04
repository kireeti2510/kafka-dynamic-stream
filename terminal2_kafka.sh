#!/bin/bash

# =============================================================================
# TERMINAL 2 - Kafka Broker
# =============================================================================
# This terminal runs the Kafka Broker service
# Start this AFTER ZooKeeper is fully running (wait 10-15 seconds)
# Keep this terminal running while using the application
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    TERMINAL 2 - KAFKA BROKER                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⏳ Make sure ZooKeeper (Terminal 1) is running first!"
echo ""
read -p "Press ENTER when ZooKeeper is ready..." 
echo ""
echo "Starting Kafka Broker..."
echo ""

# Navigate to Kafka installation
cd /opt/kafka

# Start Kafka server
bin/kafka-server-start.sh config/server.properties

# This command will keep running - DO NOT CLOSE THIS TERMINAL
