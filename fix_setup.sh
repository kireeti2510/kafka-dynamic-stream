#!/bin/bash
# Fix script for Producer-Admin connection issues

echo "========================================="
echo "FIX SCRIPT - Choose Your System"
echo "========================================="
echo ""
echo "1) Fix Producer (mount NFS)"
echo "2) Fix Admin (initialize database)"
echo "3) Exit"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "========================================="
        echo "FIXING PRODUCER SYSTEM"
        echo "========================================="
        echo ""
        
        # Get admin details
        read -p "Enter Admin system IP (192.168.191.36): " ADMIN_IP
        ADMIN_IP=${ADMIN_IP:-192.168.191.36}
        
        read -p "Enter Admin system username: " ADMIN_USER
        
        echo ""
        echo "Step 1: Creating mount point..."
        sudo mkdir -p /mnt/shared_db
        
        echo "Step 2: Installing NFS client..."
        sudo apt update
        sudo apt install -y nfs-common
        
        echo "Step 3: Testing NFS server availability..."
        showmount -e $ADMIN_IP
        
        if [ $? -ne 0 ]; then
            echo "❌ Cannot reach NFS server at $ADMIN_IP"
            echo "Make sure the Admin system has NFS server running!"
            exit 1
        fi
        
        echo "Step 4: Mounting shared database..."
        sudo mount ${ADMIN_IP}:/home/${ADMIN_USER}/shared_db /mnt/shared_db
        
        if [ $? -eq 0 ]; then
            echo "✅ NFS mounted successfully!"
            
            echo "Step 5: Adding to /etc/fstab for auto-mount..."
            if ! grep -q "/mnt/shared_db" /etc/fstab; then
                echo "${ADMIN_IP}:/home/${ADMIN_USER}/shared_db /mnt/shared_db nfs defaults 0 0" | sudo tee -a /etc/fstab
                echo "✅ Added to /etc/fstab"
            fi
            
            echo ""
            echo "Step 6: Verifying mount..."
            ls -la /mnt/shared_db/
            
            echo ""
            echo "Step 7: Updating config.json..."
            cd ~/kafka-dynamic-stream
            cat > config.json << EOF
{
  "bootstrap_servers": "192.168.191.212:9092",
  "db_path": "/mnt/shared_db/topics.db",
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_watcher_poll_interval": 5,
  "acks": 1,
  "compression_type": "gzip",
  "retries": 3,
  "auto_offset_reset": "latest"
}
EOF
            echo "✅ config.json updated"
            
            echo ""
            echo "========================================="
            echo "✅ PRODUCER FIXED!"
            echo "========================================="
            echo "Now restart your producer:"
            echo "  cd ~/kafka-dynamic-stream"
            echo "  source venv/bin/activate"
            echo "  cd producer"
            echo "  python3 producer.py"
        else
            echo "❌ Mount failed! Check the error above."
        fi
        ;;
        
    2)
        echo ""
        echo "========================================="
        echo "FIXING ADMIN SYSTEM"
        echo "========================================="
        echo ""
        
        echo "Step 1: Creating shared_db directory..."
        mkdir -p ~/shared_db
        chmod 755 ~/shared_db
        
        echo "Step 2: Installing NFS server..."
        sudo apt update
        sudo apt install -y nfs-kernel-server
        
        echo "Step 3: Configuring NFS exports..."
        SUBNET="192.168.191.0/24"
        
        if ! grep -q "shared_db" /etc/exports; then
            echo "$HOME/shared_db ${SUBNET}(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
            echo "✅ Added NFS export"
        else
            echo "✅ NFS export already configured"
        fi
        
        echo "Step 4: Applying NFS exports..."
        sudo exportfs -ra
        
        echo "Step 5: Starting NFS server..."
        sudo systemctl restart nfs-kernel-server
        sudo systemctl enable nfs-kernel-server
        
        echo "Step 6: Configuring firewall..."
        sudo ufw allow from ${SUBNET} to any port nfs
        
        echo "Step 7: Setting up database..."
        cd ~/kafka-dynamic-stream
        
        # Update config.json
        cat > config.json << EOF
{
  "bootstrap_servers": "192.168.191.212:9092",
  "db_path": "$HOME/shared_db/topics.db",
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_watcher_poll_interval": 5,
  "acks": 1,
  "compression_type": "gzip",
  "retries": 3,
  "auto_offset_reset": "latest"
}
EOF
        
        echo "Step 8: Initializing database..."
        source venv/bin/activate
        
        python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, os.getcwd())
from admin.db_setup import initialize_database

print("Creating database tables...")
initialize_database()
print("✅ Database initialized!")
PYEOF
        
        echo "Step 9: Setting permissions..."
        chmod 666 ~/shared_db/topics.db
        
        echo ""
        echo "Step 10: Verifying NFS..."
        showmount -e localhost
        
        echo ""
        echo "Step 11: Checking database..."
        sqlite3 ~/shared_db/topics.db "SELECT name FROM sqlite_master WHERE type='table';"
        
        echo ""
        echo "========================================="
        echo "✅ ADMIN FIXED!"
        echo "========================================="
        echo "Now restart your admin panel:"
        echo "  cd ~/kafka-dynamic-stream"
        echo "  source venv/bin/activate"
        echo "  cd admin"
        echo "  python3 admin_panel.py"
        ;;
        
    3)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
