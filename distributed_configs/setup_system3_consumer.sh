#!/bin/bash
# Setup Script for System 3 - Consumer
# Run this on the Consumer system

set -e

echo "============================================================"
echo "  SYSTEM 3: CONSUMER SETUP"
echo "============================================================"

# Variables - CHANGE THESE!
SYSTEM2_IP="192.168.191.212"      # Kafka Broker IP
SYSTEM4_IP="192.168.191.36"      # Admin/DB Server IP
SYSTEM4_USER="your_username"    # Username on System 4
SHARED_DB_PATH="/home/${SYSTEM4_USER}/shared_db"

echo "Configuration:"
echo "  Kafka Broker: ${SYSTEM2_IP}:9092"
echo "  DB Server: ${SYSTEM4_IP}"
echo "  Shared DB Path: ${SHARED_DB_PATH}"
echo ""
read -p "Is this correct? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Edit this script to update IP addresses"
    exit 1
fi

# 1. Install Dependencies
echo "[1/6] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nfs-common git

# 2. Create virtual environment
echo "[2/6] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. Activate venv and install Python packages
echo "[3/6] Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install kafka-python-ng python-dateutil

# 4. Mount shared database directory
echo "[4/6] Setting up shared database access..."
sudo mkdir -p /mnt/shared_db

# Check if already mounted
if ! mountpoint -q /mnt/shared_db; then
    echo "Mounting shared database from ${SYSTEM4_IP}..."
    sudo mount ${SYSTEM4_IP}:${SHARED_DB_PATH} /mnt/shared_db
    
    # Add to fstab for auto-mount on boot
    if ! grep -q "/mnt/shared_db" /etc/fstab; then
        echo "${SYSTEM4_IP}:${SHARED_DB_PATH} /mnt/shared_db nfs defaults 0 0" | sudo tee -a /etc/fstab
    fi
else
    echo "Shared database already mounted"
fi

# 5. Update configuration
echo "[5/6] Creating configuration file..."
cat > config.json << EOF
{
  "bootstrap_servers": "${SYSTEM2_IP}:9092",
  "db_path": "/mnt/shared_db/topics.db",
  "auto_offset_reset": "latest"
}
EOF

# 6. Test connectivity
echo "[6/6] Testing connectivity..."
echo "Testing Kafka broker connection..."
if timeout 3 bash -c "cat < /dev/null > /dev/tcp/${SYSTEM2_IP}/9092" 2>/dev/null; then
    echo "✓ Kafka broker is reachable at ${SYSTEM2_IP}:9092"
else
    echo "✗ Cannot reach Kafka broker at ${SYSTEM2_IP}:9092"
    echo "  Make sure Kafka is running on System 2"
fi

echo "Testing database access..."
if [ -f "/mnt/shared_db/topics.db" ]; then
    echo "✓ Database file accessible"
elif [ -d "/mnt/shared_db" ]; then
    echo "⚠ Shared directory mounted but database file not found"
    echo "  It will be created when components start"
else
    echo "✗ Cannot access shared database directory"
    echo "  Make sure NFS is configured on System 4"
fi

echo ""
echo "============================================================"
echo "  SYSTEM 3 SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "To start a consumer:"
echo "  source venv/bin/activate"
echo "  cd consumer"
echo "  python3 consumer.py 1    # User ID 1"
echo "  python3 consumer.py 2    # User ID 2 (in another terminal)"
echo ""
