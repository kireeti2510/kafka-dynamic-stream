#!/bin/bash
# ========================================
# RUN ON PRODUCER SYSTEM (192.168.191.51)
# ========================================

echo "========================================"
echo "  PRODUCER SYSTEM SETUP"
echo "  IP: 192.168.191.51"
echo "========================================"

# Step 1: Clone repository
echo ""
echo "Step 1: Cloning repository..."
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# Step 2: Update username in setup script
echo ""
echo "Step 2: Enter the username on Admin system (192.168.191.36):"
read -p "Admin system username: " ADMIN_USERNAME

sed -i "s/SYSTEM4_USER=\"your_username\"/SYSTEM4_USER=\"${ADMIN_USERNAME}\"/" distributed_configs/setup_system1_producer.sh

# Step 3: Run setup script
echo ""
echo "Step 3: Running setup script..."
cd distributed_configs
chmod +x setup_system1_producer.sh
./setup_system1_producer.sh

# Step 4: Copy config to main directory
echo ""
echo "Step 4: Setting up configuration..."
cd ~/kafka-dynamic-stream
cp distributed_configs/system1_producer_config.json config.json

echo ""
echo "========================================"
echo "  SETUP COMPLETE!"
echo "========================================"
echo ""
echo "To start the producer, run:"
echo "  cd ~/kafka-dynamic-stream"
echo "  source venv/bin/activate"
echo "  cd producer"
echo "  python3 producer.py"
echo ""
echo "Producer commands:"
echo "  create <topic_name>        - Create new topic"
echo "  send <topic_name> <msg>    - Send message"
echo "  list                       - List all topics"
echo "  quit                       - Exit"
echo ""
