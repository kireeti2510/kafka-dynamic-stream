#!/bin/bash
# Setup Script for System 4 - Admin + Database
# Run this on the Admin/Database server system

set -e

echo "============================================================"
echo "  SYSTEM 4: ADMIN + DATABASE SETUP"
echo "============================================================"

# Variables - CHANGE THESE!
# Variables - CHANGE THESE!
SYSTEM4_IP="192.168.191.36"          # This server's IP address
NETWORK_SUBNET="192.168.191.0/24"    # Your network subnet (for firewall)
SHARED_DB_DIR="$HOME/shared_db"

echo "Configuration:"
echo "  Admin Server IP: ${SYSTEM4_IP}"
echo "  Network Subnet: ${NETWORK_SUBNET}"
echo "  Shared DB Directory: ${SHARED_DB_DIR}"
echo ""
read -p "Is this correct? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Edit this script to update configuration"
    exit 1
fi

# 1. Install Dependencies
echo "[1/6] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nfs-kernel-server git

# 2. Create virtual environment
echo "[2/6] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. Activate venv and install Python packages
echo "[3/6] Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install kafka-python-ng Flask Werkzeug python-dateutil

# 4. Setup shared database directory
echo "[4/6] Setting up shared database directory..."
mkdir -p ${SHARED_DB_DIR}
chmod 755 ${SHARED_DB_DIR}

# Configure NFS export
echo "Configuring NFS server..."
NFS_EXPORT="${SHARED_DB_DIR} ${NETWORK_SUBNET}(rw,sync,no_subtree_check,no_root_squash)"

if ! grep -q "${SHARED_DB_DIR}" /etc/exports; then
    echo "${NFS_EXPORT}" | sudo tee -a /etc/exports
    echo "✓ NFS export added"
else
    echo "⚠ NFS export already configured"
fi

# Apply NFS exports
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server
sudo systemctl enable nfs-kernel-server

echo "✓ NFS server configured and started"

# 5. Configure Firewall
echo "[5/6] Configuring firewall..."
sudo ufw allow from ${NETWORK_SUBNET} to any port nfs comment 'NFS Server'
sudo ufw allow from ${NETWORK_SUBNET} to any port 5000 comment 'Web UI'
sudo ufw --force enable

echo "✓ Firewall configured"

# 6. Update configuration
echo "[6/6] Creating configuration file..."
cat > config.json << EOF
{
  "db_path": "${SHARED_DB_DIR}/topics.db",
  "web_ui_host": "0.0.0.0",
  "web_ui_port": 5000
}
EOF

# Initialize database
echo "Initializing database..."
source venv/bin/activate
python3 -c "
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
# Update DB_PATH to use shared directory
import admin.db_setup as db
db.DB_PATH = '${SHARED_DB_DIR}/topics.db'
db.initialize_database()
"

echo ""
echo "============================================================"
echo "  SYSTEM 4 SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Shared Database: ${SHARED_DB_DIR}/topics.db"
echo "NFS Export: ${SHARED_DB_DIR} → ${NETWORK_SUBNET}"
echo ""
echo "To start the admin panel:"
echo "  source venv/bin/activate"
echo "  cd admin"
echo "  python3 admin_panel.py"
echo ""
echo "To start the web UI:"
echo "  source venv/bin/activate"
echo "  cd web"
echo "  python3 app.py"
echo "  Access at: http://${SYSTEM4_IP}:5000"
echo ""
echo "To verify NFS export:"
echo "  showmount -e localhost"
echo ""
