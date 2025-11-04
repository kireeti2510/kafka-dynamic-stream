#!/bin/bash

# =============================================================================
# TERMINAL 1 - ZooKeeper
# =============================================================================
# This terminal runs the ZooKeeper service required by Kafka
# Keep this terminal running while using the application
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    TERMINAL 1 - ZOOKEEPER                             ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting ZooKeeper..."
echo ""

# Navigate to Kafka installation
cd /opt/kafka

# Start ZooKeeper server
bin/zookeeper-server-start.sh config/zookeeper.properties

# This command will keep running - DO NOT CLOSE THIS TERMINAL
