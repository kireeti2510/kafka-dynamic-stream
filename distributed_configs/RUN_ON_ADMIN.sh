#!/bin/bash
# ========================================
# RUN ON ADMIN SYSTEM (192.168.191.36)
# ========================================

echo "========================================"
echo "  ADMIN + DATABASE SYSTEM SETUP"
echo "  IP: 192.168.191.36"
echo "========================================"

# Step 1: Clone repository
echo ""
echo "Step 1: Cloning repository..."
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# Step 2: Run setup script
echo ""
echo "Step 2: Running setup script..."
cd distributed_configs
chmod +x setup_system4_admin.sh
./setup_system4_admin.sh

# Step 3: Copy config to main directory
echo ""
echo "Step 3: Setting up configuration..."
cd ~/kafka-dynamic-stream
cp distributed_configs/system4_admin_config.json config.json

echo ""
echo "========================================"
echo "  SETUP COMPLETE!"
echo "========================================"
echo ""
echo "NFS server is running and sharing ~/shared_db/"
echo ""
echo "To start the Admin Panel (Terminal 1):"
echo "  cd ~/kafka-dynamic-stream"
echo "  source venv/bin/activate"
echo "  cd admin"
echo "  python3 admin_panel.py"
echo ""
echo "To start the Web UI (Terminal 2):"
echo "  cd ~/kafka-dynamic-stream"
echo "  source venv/bin/activate"
echo "  cd web"
echo "  python3 app.py"
echo ""
echo "Access Web UI at: http://192.168.191.36:5000"
echo ""
echo "Admin Panel commands:"
echo "  1 - View all topics"
echo "  2 - Approve pending topic"
echo "  3 - Delete topic"
echo "  4 - View user subscriptions"
echo "  5 - Exit"
echo ""
