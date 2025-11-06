# 🚀 EXACT COMMANDS TO RUN - DISTRIBUTED SETUP

## ⚠️ IMPORTANT: EXECUTION ORDER

**Run in this order:**
1. **System 4 FIRST** (Database Server)
2. **System 2 SECOND** (Kafka Broker)
3. **System 1 & 3** (Any order)

---

## 📋 SYSTEM 4: ADMIN + DATABASE (Run FIRST!)

### Terminal Commands:
```bash
# 1. Get IP address
hostname -I | awk '{print $1}'
# Write it down: ________________

# 2. Clone repo
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# 3. Edit setup script
nano distributed_configs/setup_system4_admin.sh
# Edit lines 10-12:
#   SYSTEM4_IP="YOUR_IP_HERE"
#   NETWORK_SUBNET="YOUR_SUBNET/24"
# Save: Ctrl+O, Enter, Ctrl+X

# 4. Run setup
cd distributed_configs
chmod +x setup_system4_admin.sh
./setup_system4_admin.sh
# Wait for completion ✓

# 5. Verify NFS
showmount -e localhost
ls -la ~/shared_db/
```

### Start Services (2 terminals needed):

**Terminal 1 - Admin Panel:**
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd admin
python3 admin_panel.py
```

**Terminal 2 - Web UI:**
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd web
python3 app.py
# Access at: http://YOUR_SYSTEM4_IP:5000
```

---

## ⚙️ SYSTEM 2: KAFKA BROKER (Run SECOND!)

### Terminal Commands:
```bash
# 1. Get IP address
hostname -I | awk '{print $1}'
# Write it down: ________________

# 2. Clone repo
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# 3. Edit setup script
nano distributed_configs/setup_system2_kafka.sh
# Edit line 10:
#   SYSTEM2_IP="YOUR_IP_HERE"
# Save: Ctrl+O, Enter, Ctrl+X

# 4. Run setup
cd distributed_configs
chmod +x setup_system2_kafka.sh
./setup_system2_kafka.sh
# This takes 5-10 minutes (installs Kafka)
# When asked "Start Kafka now?", answer: y
# Wait for completion ✓

# 5. Verify Kafka is running
sudo systemctl status kafka
sudo systemctl status zookeeper
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

**Kafka starts automatically via systemd!** No manual start needed.

---

## 📤 SYSTEM 1: PRODUCER (Run THIRD!)

### Terminal Commands:
```bash
# 1. Get IP address
hostname -I | awk '{print $1}'

# 2. Clone repo
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# 3. Edit setup script
nano distributed_configs/setup_system1_producer.sh
# Edit lines 10-13:
#   SYSTEM2_IP="192.168.1.20"      ← System 2 IP
#   SYSTEM4_IP="192.168.1.40"      ← System 4 IP
#   SYSTEM4_USER="username"        ← System 4 username
# Save: Ctrl+O, Enter, Ctrl+X

# 4. Run setup
cd distributed_configs
chmod +x setup_system1_producer.sh
./setup_system1_producer.sh
# Wait for completion ✓

# 5. Verify connectivity
telnet SYSTEM2_IP 9092
# Press Ctrl+] then type 'quit'

ls -la /mnt/shared_db/

# 6. Start producer
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd producer
python3 producer.py
```

**Producer Commands:**
```
> create news_updates      # Create topic
> list                     # List all topics
> send news_updates Hello! # Send message (after approval)
> quit                     # Exit
```

---

## 📥 SYSTEM 3: CONSUMER (Run FOURTH!)

### Terminal Commands:
```bash
# 1. Get IP address
hostname -I | awk '{print $1}'

# 2. Clone repo
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream

# 3. Edit setup script
nano distributed_configs/setup_system3_consumer.sh
# Edit lines 10-13:
#   SYSTEM2_IP="192.168.1.20"      ← System 2 IP
#   SYSTEM4_IP="192.168.1.40"      ← System 4 IP
#   SYSTEM4_USER="username"        ← System 4 username
# Save: Ctrl+O, Enter, Ctrl+X

# 4. Run setup
cd distributed_configs
chmod +x setup_system3_consumer.sh
./setup_system3_consumer.sh
# Wait for completion ✓

# 5. Verify connectivity
telnet SYSTEM2_IP 9092
# Press Ctrl+] then type 'quit'

ls -la /mnt/shared_db/

# 6. Start consumer
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd consumer
python3 consumer.py 1
```

**Consumer Commands:**
```
> list                        # List active topics
> subscribe news_updates      # Subscribe to topic
> subscribed                  # Show your subscriptions
> quit                        # Exit
```

---

## 🧪 COMPLETE END-TO-END TEST

### Step 1: Create Topic (System 1 - Producer)
```
> create news_updates
✓ Topic 'news_updates' created with status: PENDING
```

### Step 2: Approve Topic (System 4 - Admin Panel)
```
Enter your choice: 2
>> news_updates
✓ Approved: news_updates

# Topic Watcher (System 1) will:
# - Detect approval
# - Create in Kafka
# - Update to 'active'
```

### Step 3: Subscribe (System 3 - Consumer)
```
> subscribe news_updates
✓ Subscribed to 'news_updates'
📋 Active subscriptions: news_updates
```

### Step 4: Send Message (System 1 - Producer)
```
> send news_updates Hello from distributed Kafka!
✓ Message queued for topic 'news_updates'
✓ Publisher: Sent to 'news_updates' [partition 1, offset 0]
```

### Step 5: Receive Message (System 3 - Consumer)
```
📨 [news_updates] Message received:
   Content: Hello from distributed Kafka!
   Timestamp: 2025-11-06 10:30:45
   Partition: 1 | Offset: 0
```

### Step 6: Monitor (System 4 - Web UI)
```
Open browser: http://SYSTEM4_IP:5000
- See all topics with statuses
- View user subscriptions
- Real-time updates every 5 seconds
```

---

## 🔧 TROUBLESHOOTING

### Cannot reach Kafka (System 2)
```bash
# On System 2:
sudo systemctl status kafka
sudo ufw allow 9092/tcp
sudo systemctl restart kafka

# From System 1 or 3:
telnet SYSTEM2_IP 9092
```

### Cannot mount database (System 1 or 3)
```bash
# Check NFS on System 4:
sudo systemctl status nfs-kernel-server
showmount -e SYSTEM4_IP

# Manual mount on System 1 or 3:
sudo mount SYSTEM4_IP:/home/USERNAME/shared_db /mnt/shared_db
```

### Database locked
```bash
# On System 4:
chmod 666 ~/shared_db/topics.db
```

---

## 📊 VERIFICATION CHECKLIST

Before starting applications:

**System 4:**
- [ ] NFS server running: `sudo systemctl status nfs-kernel-server`
- [ ] Database exists: `ls -la ~/shared_db/topics.db`
- [ ] Exports configured: `showmount -e localhost`

**System 2:**
- [ ] ZooKeeper running: `sudo systemctl status zookeeper`
- [ ] Kafka running: `sudo systemctl status kafka`
- [ ] Port 9092 open: `sudo netstat -tlnp | grep 9092`

**System 1:**
- [ ] Kafka reachable: `telnet SYSTEM2_IP 9092`
- [ ] Database mounted: `ls -la /mnt/shared_db/`
- [ ] Config exists: `cat config.json`

**System 3:**
- [ ] Kafka reachable: `telnet SYSTEM2_IP 9092`
- [ ] Database mounted: `ls -la /mnt/shared_db/`
- [ ] Config exists: `cat config.json`

---

## 🎯 QUICK REFERENCE

| System | IP Example | Runs | Port | Start Command |
|--------|------------|------|------|---------------|
| System 4 | 192.168.1.40 | Admin + DB | 5000, NFS | `python3 admin_panel.py` |
| System 2 | 192.168.1.20 | Kafka | 9092, 2181 | Auto-starts via systemd |
| System 1 | 192.168.1.10 | Producer | - | `python3 producer.py` |
| System 3 | 192.168.1.30 | Consumer | - | `python3 consumer.py 1` |

---

## 💡 TIPS

1. **Always start System 4 first** - It provides the database
2. **Start System 2 second** - It provides Kafka broker
3. **Test connectivity** before starting apps
4. **Use Web UI** for easy monitoring
5. **Check logs** if something fails:
   - Kafka: `sudo journalctl -u kafka -f`
   - NFS: `sudo journalctl -u nfs-kernel-server -f`

---

## 📞 GETTING HELP

If stuck, check:
- `COMMANDS_SYSTEM1_PRODUCER.sh` - Detailed System 1 commands
- `COMMANDS_SYSTEM2_KAFKA.sh` - Detailed System 2 commands
- `COMMANDS_SYSTEM3_CONSUMER.sh` - Detailed System 3 commands
- `COMMANDS_SYSTEM4_ADMIN.sh` - Detailed System 4 commands
- `QUICKSTART_DISTRIBUTED.md` - Full guide with troubleshooting

---

**Ready? Start with System 4!** 🚀
