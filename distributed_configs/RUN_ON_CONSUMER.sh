#!/bin/bash
# ========================================
# RUN ON CONSUMER SYSTEM (192.168.191.169)
# ========================================

echo "========================================"
echo "  CONSUMER SYSTEM SETUP"
echo "  IP: 192.168.191.169"
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

sed -i "s/SYSTEM4_USER=\"your_username\"/SYSTEM4_USER=\"${ADMIN_USERNAME}\"/" distributed_configs/setup_system3_consumer.sh

# Step 3: Run setup script
echo ""
echo "Step 3: Running setup script..."
cd distributed_configs
chmod +x setup_system3_consumer.sh
./setup_system3_consumer.sh

# Step 4: Copy config to main directory
echo ""
echo "Step 4: Setting up configuration..."
cd ~/kafka-dynamic-stream
cp distributed_configs/system3_consumer_config.json config.json

echo ""
echo "========================================"
echo "  SETUP COMPLETE!"
echo "========================================"
echo ""
echo "To start a consumer, run:"
echo "  cd ~/kafka-dynamic-stream"
echo "  source venv/bin/activate"
echo "  cd consumer"
echo "  python3 consumer.py 1"
echo ""
echo "Consumer commands:"
echo "  list                       - List all active topics"
echo "  subscribe <topic_name>     - Subscribe to topic"
echo "  subscribed                 - Show your subscriptions"
echo "  unsubscribe <topic_name>   - Unsubscribe from topic"
echo "  quit                       - Exit"
echo ""
echo "To run multiple consumers, use different user IDs:"
echo "  python3 consumer.py 2"
echo "  python3 consumer.py 3"
echo ""
