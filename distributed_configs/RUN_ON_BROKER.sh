#!/bin/bash
# ========================================
# RUN ON KAFKA BROKER (192.168.191.212)
# ========================================

echo "========================================"
echo "  KAFKA BROKER SETUP"
echo "  IP: 192.168.191.212"
echo "========================================"

# Step 1: Clone repository
echo ""
echo "Step 1: Cloning repository..."
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# Step 2: Run setup script
echo ""
echo "Step 2: Running Kafka setup script..."
echo "This will install Java, Kafka, and configure services..."
cd distributed_configs
chmod +x setup_system2_kafka.sh
./setup_system2_kafka.sh

# When prompted "Start Kafka now? (y/n)", answer 'y'

echo ""
echo "========================================"
echo "  SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Kafka is now running as a systemd service!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status kafka      - Check Kafka status"
echo "  sudo systemctl status zookeeper  - Check ZooKeeper status"
echo "  sudo systemctl restart kafka     - Restart Kafka"
echo "  sudo systemctl stop kafka        - Stop Kafka"
echo "  sudo journalctl -u kafka -f      - View Kafka logs"
echo ""
echo "List topics:"
echo "  /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092"
echo ""
echo "View topic details:"
echo "  /opt/kafka/bin/kafka-topics.sh --describe --topic <topic_name> --bootstrap-server localhost:9092"
echo ""
