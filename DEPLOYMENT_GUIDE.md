# 🚀 DEPLOYMENT GUIDE - YOUR NETWORK SETUP

## 📊 Your Network Configuration

| System | IP Address | Role | Ports |
|--------|------------|------|-------|
| **System 1** | 192.168.191.51 | Producer | - |
| **System 2** | 192.168.191.212 | Kafka Broker | 9092, 2181 |
| **System 3** | 192.168.191.169 | Consumer | - |
| **System 4** | 192.168.191.36 | Admin + Database | 5000, NFS |

**Network Subnet:** 192.168.191.0/24

---

## ⚡ QUICK START - Run These Commands

### 🔴 STEP 1: System 4 (Admin + Database) - 192.168.191.36
**RUN THIS FIRST!**

```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream/distributed_configs
chmod +x RUN_ON_ADMIN.sh
./RUN_ON_ADMIN.sh
```

After setup completes, start services in **2 separate terminals**:

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
```

**Access Web UI:** http://192.168.191.36:5000

---

### 🟡 STEP 2: System 2 (Kafka Broker) - 192.168.191.212
**RUN THIS SECOND!**

```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream/distributed_configs
chmod +x RUN_ON_BROKER.sh
./RUN_ON_BROKER.sh
```

When prompted "Start Kafka now? (y/n)", answer: **y**

Kafka will run automatically as a systemd service. **No manual start needed!**

**Verify Kafka is running:**
```bash
sudo systemctl status kafka
sudo systemctl status zookeeper
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

---

### 🟢 STEP 3: System 1 (Producer) - 192.168.191.51
**RUN THIS THIRD!**

```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream/distributed_configs
chmod +x RUN_ON_PRODUCER.sh
./RUN_ON_PRODUCER.sh
```

When prompted, enter the **username** of System 4 (192.168.191.36).

**Start Producer:**
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd producer
python3 producer.py
```

**Producer Commands:**
```
> create news_topic       # Create topic (pending approval)
> list                    # List all topics
> send news_topic Hello!  # Send message (after approval)
> quit                    # Exit
```

---

### 🔵 STEP 4: System 3 (Consumer) - 192.168.191.169
**RUN THIS FOURTH!**

```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream/distributed_configs
chmod +x RUN_ON_CONSUMER.sh
./RUN_ON_CONSUMER.sh
```

When prompted, enter the **username** of System 4 (192.168.191.36).

**Start Consumer:**
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd consumer
python3 consumer.py 1
```

**Consumer Commands:**
```
> list                      # List active topics
> subscribe news_topic      # Subscribe to topic
> subscribed                # Show your subscriptions
> quit                      # Exit
```

---

## 🧪 END-TO-END TEST

### 1️⃣ Create Topic (System 1 - Producer)
```
> create news_updates
✓ Topic 'news_updates' created with status: PENDING
```

### 2️⃣ Approve Topic (System 4 - Admin Panel)
```
Enter your choice: 2
>> news_updates
✓ Approved: news_updates
```

Wait 5-10 seconds for Topic Watcher to create it in Kafka.

### 3️⃣ Subscribe to Topic (System 3 - Consumer)
```
> subscribe news_updates
✓ Subscribed to 'news_updates'
```

### 4️⃣ Send Message (System 1 - Producer)
```
> send news_updates Hello from distributed Kafka!
✓ Message queued for topic 'news_updates'
```

### 5️⃣ Receive Message (System 3 - Consumer)
You should see:
```
📨 [news_updates] Message received:
   Content: Hello from distributed Kafka!
   Timestamp: 2025-11-06 15:30:00
   Partition: 0 | Offset: 0
```

### 6️⃣ Monitor (System 4 - Web UI)
Open browser: **http://192.168.191.36:5000**

---

## 🔧 TROUBLESHOOTING

### Can't connect to Kafka (from System 1 or 3)
```bash
# Test connectivity
telnet 192.168.191.212 9092
# Press Ctrl+] then type 'quit'

# On System 2, check Kafka status
sudo systemctl status kafka
sudo journalctl -u kafka -f

# Check firewall on System 2
sudo ufw allow 9092/tcp
sudo ufw allow 2181/tcp
sudo systemctl restart kafka
```

### Can't mount database (from System 1 or 3)
```bash
# On System 4, verify NFS is running
sudo systemctl status nfs-kernel-server
showmount -e 192.168.191.36

# On System 1 or 3, check mount
ls -la /mnt/shared_db/

# Manual mount if needed
sudo mount 192.168.191.36:/home/USERNAME/shared_db /mnt/shared_db
```

### Database permission errors
```bash
# On System 4
chmod 666 ~/shared_db/topics.db
ls -la ~/shared_db/
```

### Kafka management commands (System 2)
```bash
# List all topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe topic
/opt/kafka/bin/kafka-topics.sh --describe --topic news_updates --bootstrap-server localhost:9092

# Delete topic (if needed)
/opt/kafka/bin/kafka-topics.sh --delete --topic news_updates --bootstrap-server localhost:9092

# View Kafka logs
sudo journalctl -u kafka -f

# Restart Kafka
sudo systemctl restart kafka
```

---

## 📋 PRE-DEPLOYMENT CHECKLIST

**Before starting:**
- [ ] All 4 systems are on the same network (192.168.191.0/24)
- [ ] All systems can ping each other
- [ ] You know the username on System 4
- [ ] You have sudo access on all systems

**System 4 (Admin):**
- [ ] Repository cloned
- [ ] Setup script run
- [ ] Admin panel running
- [ ] Web UI running (http://192.168.191.36:5000 accessible)
- [ ] NFS server running: `sudo systemctl status nfs-kernel-server`

**System 2 (Kafka):**
- [ ] Repository cloned
- [ ] Setup script run
- [ ] Kafka running: `sudo systemctl status kafka`
- [ ] ZooKeeper running: `sudo systemctl status zookeeper`
- [ ] Port 9092 accessible

**System 1 (Producer):**
- [ ] Repository cloned
- [ ] Setup script run (with correct System 4 username)
- [ ] Database mounted: `ls -la /mnt/shared_db/`
- [ ] Can connect to Kafka: `telnet 192.168.191.212 9092`
- [ ] config.json exists

**System 3 (Consumer):**
- [ ] Repository cloned
- [ ] Setup script run (with correct System 4 username)
- [ ] Database mounted: `ls -la /mnt/shared_db/`
- [ ] Can connect to Kafka: `telnet 192.168.191.212 9092`
- [ ] config.json exists

---

## 🎯 SYSTEM-SPECIFIC FILES

All configurations are pre-set for your network:

- **System 1 Config:** `distributed_configs/system1_producer_config.json`
  - Kafka: 192.168.191.212:9092
  - Database: /mnt/shared_db/topics.db

- **System 2 Config:** `distributed_configs/system2_kafka_server.properties`
  - Listener: 192.168.191.212:9092
  - Advertised: 192.168.191.212:9092

- **System 3 Config:** `distributed_configs/system3_consumer_config.json`
  - Kafka: 192.168.191.212:9092
  - Database: /mnt/shared_db/topics.db

- **System 4 Config:** `distributed_configs/system4_admin_config.json`
  - Web UI: 192.168.191.36:5000
  - Database: ~/shared_db/topics.db

---

## 💡 IMPORTANT NOTES

1. **Order matters:** System 4 → System 2 → Systems 1 & 3
2. **System 4 username:** Required for NFS mounting on Systems 1 & 3
3. **Kafka auto-starts:** On System 2 via systemd (no manual start)
4. **Web UI:** Access at http://192.168.191.36:5000
5. **Multiple consumers:** Use different user IDs (1, 2, 3, etc.)

---

## 🆘 GET HELP

Full documentation in `distributed_configs/`:
- `EXECUTION_ORDER.md` - Detailed step-by-step guide
- `QUICKSTART_DISTRIBUTED.md` - Quick reference
- `DISTRIBUTED_SETUP.md` - Complete setup documentation

---

**Ready to deploy? Start with System 4!** 🚀
