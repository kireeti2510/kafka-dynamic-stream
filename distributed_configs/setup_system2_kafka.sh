#!/bin/bash
# Setup Script for System 2 - Kafka Broker
# Run this on the Kafka Broker system

set -e

echo "============================================================"
echo "  SYSTEM 2: KAFKA BROKER SETUP"
echo "============================================================"

# Variables - CHANGE THIS!
SYSTEM2_IP="192.168.1.20"      # This system's IP address

echo "Configuration:"
echo "  Kafka Broker IP: ${SYSTEM2_IP}"
echo "  Kafka Port: 9092"
echo "  ZooKeeper Port: 2181"
echo ""
read -p "Is the IP address correct? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Edit this script to update SYSTEM2_IP"
    exit 1
fi

# 1. Install Java
echo "[1/7] Installing Java..."
sudo apt update
sudo apt install -y openjdk-11-jdk

java -version

# 2. Download and Install Kafka
echo "[2/7] Installing Kafka..."
if [ ! -d "/opt/kafka" ]; then
    cd /opt
    echo "Downloading Kafka..."
    sudo wget -q https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
    echo "Extracting..."
    sudo tar -xzf kafka_2.13-3.6.0.tgz
    sudo mv kafka_2.13-3.6.0 kafka
    sudo rm kafka_2.13-3.6.0.tgz
    echo "✓ Kafka installed to /opt/kafka"
else
    echo "✓ Kafka already installed"
fi

# 3. Configure Kafka for network access
echo "[3/7] Configuring Kafka server..."
sudo cp /opt/kafka/config/server.properties /opt/kafka/config/server.properties.backup

sudo tee /opt/kafka/config/server.properties > /dev/null << EOF
# Server Basics
broker.id=0

# Socket Server Settings
listeners=PLAINTEXT://${SYSTEM2_IP}:9092
advertised.listeners=PLAINTEXT://${SYSTEM2_IP}:9092
listener.security.protocol.map=PLAINTEXT:PLAINTEXT

num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Log Basics
log.dirs=/tmp/kafka-logs
num.partitions=3
num.recovery.threads.per.data.dir=1

# Internal Topic Settings
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1

# Log Retention Policy
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000

# ZooKeeper
zookeeper.connect=localhost:2181
zookeeper.connection.timeout.ms=18000

# Group Coordinator Settings
group.initial.rebalance.delay.ms=0

# Disable auto topic creation
auto.create.topics.enable=false
EOF

echo "✓ Kafka server configured"

# 4. Configure ZooKeeper
echo "[4/7] Configuring ZooKeeper..."
sudo tee /opt/kafka/config/zookeeper.properties > /dev/null << EOF
# ZooKeeper Settings
dataDir=/tmp/zookeeper
clientPort=2181
maxClientCnxns=0
admin.enableServer=false
EOF

echo "✓ ZooKeeper configured"

# 5. Configure Firewall
echo "[5/7] Configuring firewall..."
sudo ufw allow 9092/tcp comment 'Kafka Broker'
sudo ufw allow 2181/tcp comment 'ZooKeeper'
sudo ufw --force enable

echo "✓ Firewall configured"

# 6. Create systemd services (optional but recommended)
echo "[6/7] Creating systemd services..."

# ZooKeeper service
sudo tee /etc/systemd/system/zookeeper.service > /dev/null << EOF
[Unit]
Description=Apache ZooKeeper
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
ExecStop=/opt/kafka/bin/zookeeper-server-stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Kafka service
sudo tee /etc/systemd/system/kafka.service > /dev/null << EOF
[Unit]
Description=Apache Kafka
After=zookeeper.service network.target
Requires=zookeeper.service

[Service]
Type=simple
User=$USER
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo "✓ Systemd services created"

# 7. Start services
echo "[7/7] Starting services..."

read -p "Start Kafka and ZooKeeper now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl start zookeeper
    sleep 5
    sudo systemctl start kafka
    sleep 5
    
    # Enable auto-start on boot
    sudo systemctl enable zookeeper
    sudo systemctl enable kafka
    
    echo "✓ Services started and enabled"
    
    # Check status
    echo ""
    echo "Service Status:"
    sudo systemctl status zookeeper --no-pager -l
    echo ""
    sudo systemctl status kafka --no-pager -l
else
    echo "Skipping service start. To start manually:"
    echo "  sudo systemctl start zookeeper"
    echo "  sudo systemctl start kafka"
fi

echo ""
echo "============================================================"
echo "  SYSTEM 2 SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Kafka Broker running at: ${SYSTEM2_IP}:9092"
echo ""
echo "To check status:"
echo "  sudo systemctl status kafka"
echo "  sudo systemctl status zookeeper"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u kafka -f"
echo "  sudo journalctl -u zookeeper -f"
echo ""
echo "To test from another system:"
echo "  telnet ${SYSTEM2_IP} 9092"
echo ""
