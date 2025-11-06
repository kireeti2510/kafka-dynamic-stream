#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  SYSTEM 4: ADMIN + DATABASE - TERMINAL COMMANDS
# ═══════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════"
echo "  SYSTEM 4: ADMIN + DATABASE SETUP COMMANDS"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Copy and paste these commands in order:"
echo ""

cat << 'EOF'

# ──────────────────────────────────────────────────────────────
# STEP 1: Get Your System's IP Address
# ──────────────────────────────────────────────────────────────
hostname -I | awk '{print $1}'

# ✏️ WRITE DOWN:
# System 4 (This System) IP: ________________
# Your username: ________________
# Your network subnet: ________________ (e.g., 192.168.1.0/24)


# ──────────────────────────────────────────────────────────────
# STEP 2: Clone Repository
# ──────────────────────────────────────────────────────────────
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream


# ──────────────────────────────────────────────────────────────
# STEP 3: Edit Setup Script with Your Configuration
# ──────────────────────────────────────────────────────────────
nano distributed_configs/setup_system4_admin.sh

# ✏️ EDIT THESE LINES (around line 10-12):
# SYSTEM4_IP="192.168.1.40"        ← Change to YOUR IP
# NETWORK_SUBNET="192.168.1.0/24"  ← Change to YOUR network subnet

# Press: Ctrl+O (save), Enter, Ctrl+X (exit)


# ──────────────────────────────────────────────────────────────
# STEP 4: Run Setup Script
# ──────────────────────────────────────────────────────────────
cd distributed_configs
chmod +x setup_system4_admin.sh
./setup_system4_admin.sh

# ⏳ Wait for setup to complete...
# ✅ Setup will:
#    - Install Python dependencies
#    - Configure NFS server
#    - Create shared database directory
#    - Set up firewall
#    - Initialize database


# ──────────────────────────────────────────────────────────────
# STEP 5: Verify NFS Server
# ──────────────────────────────────────────────────────────────
# Check NFS is running
sudo systemctl status nfs-kernel-server

# Check exports
sudo exportfs -v
showmount -e localhost

# Check shared directory
ls -la ~/shared_db/


# ══════════════════════════════════════════════════════════════
# TERMINAL 1: ADMIN PANEL
# ══════════════════════════════════════════════════════════════
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd admin
python3 admin_panel.py

# ──────────────────────────────────────────────────────────────
# ADMIN PANEL MENU:
# ──────────────────────────────────────────────────────────────
# 1. View Pending Topics
# 2. Approve Topics
# 3. Reject Topics
# 4. View All Topics
# 5. View User Subscriptions
# 6. Exit


# ══════════════════════════════════════════════════════════════
# TERMINAL 2: WEB UI (Open a new terminal)
# ══════════════════════════════════════════════════════════════
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd web
python3 app.py

# 🌐 Access Web UI at: http://SYSTEM4_IP:5000
# Example: http://192.168.1.40:5000


# ══════════════════════════════════════════════════════════════
# WORKFLOW EXAMPLE:
# ══════════════════════════════════════════════════════════════

# When System 1 creates a topic "news_updates":

# ADMIN PANEL (Terminal 1):
# 1. Select option: 1 (View Pending Topics)
#    You'll see: news_updates [pending]
#
# 2. Select option: 2 (Approve Topics)
#    Enter: news_updates
#    Result: ✓ Approved: news_updates
#
# 3. Topic Watcher on System 1 will:
#    - Detect approval
#    - Create topic in Kafka (System 2)
#    - Update status to 'active'
#
# 4. View all topics (option 4):
#    You'll see: news_updates [active]

# WEB UI (Browser):
# - Open http://SYSTEM4_IP:5000
# - See real-time topic statuses
# - View user subscriptions
# - Monitor system activity


# ══════════════════════════════════════════════════════════════
# DATABASE MANAGEMENT
# ══════════════════════════════════════════════════════════════

# View database directly:
sqlite3 ~/shared_db/topics.db

# SQL commands:
# .tables                           - List tables
# .schema topics                    - View topics table structure
# SELECT * FROM topics;             - View all topics
# SELECT * FROM user_subscriptions; - View subscriptions
# .quit                             - Exit sqlite


# Check who's accessing the database via NFS:
sudo netstat -an | grep :2049


# ══════════════════════════════════════════════════════════════
# NFS SERVER MANAGEMENT
# ══════════════════════════════════════════════════════════════

# Start NFS server:
sudo systemctl start nfs-kernel-server

# Stop NFS server:
sudo systemctl stop nfs-kernel-server

# Restart NFS server:
sudo systemctl restart nfs-kernel-server

# Check status:
sudo systemctl status nfs-kernel-server

# View current exports:
sudo exportfs -v

# Reload exports (after editing /etc/exports):
sudo exportfs -ra

# View connected clients:
sudo netstat -an | grep :2049


# ══════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ══════════════════════════════════════════════════════════════

# If NFS not accessible from other systems:
sudo ufw status
sudo ufw allow from 192.168.1.0/24 to any port nfs
sudo systemctl restart nfs-kernel-server

# If Web UI not accessible:
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Check database file permissions:
ls -la ~/shared_db/topics.db
chmod 666 ~/shared_db/topics.db  # If needed

# Test NFS from another system:
# showmount -e SYSTEM4_IP

EOF
