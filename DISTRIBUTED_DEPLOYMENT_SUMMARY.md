# ✅ Distributed Setup Complete!

## 🎉 What I Created For You

I've just set up your Kafka Dynamic Stream project for **distributed deployment across 4 systems**!

---

## 📦 New Files Created

### 📁 `distributed_configs/` Directory

**Automated Setup Scripts:**
1. ✅ `setup_system1_producer.sh` - Auto-setup for Producer system
2. ✅ `setup_system2_kafka.sh` - Auto-setup for Kafka Broker system  
3. ✅ `setup_system3_consumer.sh` - Auto-setup for Consumer system
4. ✅ `setup_system4_admin.sh` - Auto-setup for Admin + Database system

**Configuration Templates:**
5. ✅ `system1_producer_config.json` - Producer config
6. ✅ `system2_kafka_server.properties` - Kafka broker config
7. ✅ `system3_consumer_config.json` - Consumer config
8. ✅ `system4_admin_config.json` - Admin config

**Documentation:**
9. ✅ `README_DISTRIBUTED.md` - Main distributed setup guide
10. ✅ `QUICKSTART_DISTRIBUTED.md` - **START HERE** quick guide
11. ✅ `db_setup_distributed.py` - Modified database module

**Project Root:**
12. ✅ `DISTRIBUTED_SETUP.md` - Detailed setup documentation

---

## 🌐 System Distribution

```
┌─────────────────────────────────────────────────────────┐
│                Your Network (192.168.1.x)               │
│                                                         │
│  System 1          System 2          System 3          │
│  Producer     →    Kafka Broker  →   Consumer          │
│  192.168.1.10      192.168.1.20      192.168.1.30      │
│       ↓                                    ↓            │
│       └──────→  System 4  ←───────────────┘            │
│              Admin + Database                           │
│              192.168.1.40                               │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 How to Deploy (3 Simple Steps)

### Step 1: Get IP Addresses

On each system, run:
```bash
hostname -I | awk '{print $1}'
```

Record your actual IPs:
- System 1 (Producer): `_______________`
- System 2 (Kafka Broker): `_______________`  
- System 3 (Consumer): `_______________`
- System 4 (Admin + DB): `_______________`

---

### Step 2: Clone Repo on All 4 Systems

```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream/distributed_configs
```

---

### Step 3: Edit & Run Setup Scripts

#### On Each System:

1. **Edit the setup script** with your actual IP addresses:
   ```bash
   nano setup_systemX_*.sh
   # Update SYSTEM2_IP, SYSTEM4_IP, etc.
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup_systemX_*.sh
   ./setup_systemX_*.sh
   ```

**⚠️ IMPORTANT ORDER:**
1. Run System 4 setup FIRST (database server)
2. Run System 2 setup SECOND (Kafka broker)
3. Run System 1 and 3 (any order)

---

## 📖 Documentation

### Quick Start
**→ Read `distributed_configs/QUICKSTART_DISTRIBUTED.md` first!**

This has:
- ✅ Complete step-by-step instructions
- ✅ Troubleshooting guide
- ✅ Test procedures
- ✅ Network diagram

### Detailed Guide
**→ See `DISTRIBUTED_SETUP.md` for advanced setup**

This includes:
- Database sharing options (NFS vs PostgreSQL)
- Network configuration details
- Firewall rules
- Service management

---

## 🎯 What Each System Does

### System 1: Producer (192.168.1.10)
- **Runs:** `producer.py` with 3 threads
- **Creates:** Topic requests
- **Publishes:** Messages to Kafka
- **Connects to:**
  - Kafka on System 2:9092
  - Database on System 4 via NFS

### System 2: Kafka Broker (192.168.1.20)
- **Runs:** Kafka + ZooKeeper
- **Ports:** 9092 (Kafka), 2181 (ZooKeeper)
- **Purpose:** Central message hub
- **Auto-creates:** NO - topics require approval

### System 3: Consumer (192.168.1.30)
- **Runs:** `consumer.py` (can run multiple)
- **Subscribes:** Dynamically to topics
- **Receives:** Messages from Kafka
- **Connects to:**
  - Kafka on System 2:9092
  - Database on System 4 via NFS

### System 4: Admin + Database (192.168.1.40)
- **Runs:** 
  - `admin_panel.py` - Approve/reject topics
  - `app.py` - Web UI at http://192.168.1.40:5000
  - NFS server - Shares SQLite database
- **Provides:** Central database for all systems

---

## 🔧 Setup Scripts Features

Each script automatically:
- ✅ Installs all dependencies
- ✅ Configures network settings
- ✅ Sets up firewall rules
- ✅ Creates configuration files
- ✅ Tests connectivity
- ✅ Provides status output

**System 2 script also:**
- ✅ Installs Java
- ✅ Downloads and installs Kafka
- ✅ Creates systemd services
- ✅ Starts Kafka and ZooKeeper

---

## 💾 Database Sharing

**Using NFS (default):**
- System 4 exports `~/shared_db/` via NFS
- Systems 1 & 3 mount it at `/mnt/shared_db/`
- All systems access same `topics.db` file

**Alternative: PostgreSQL (recommended for production)**
- See `DISTRIBUTED_SETUP.md` for PostgreSQL setup
- Better for concurrent access
- More reliable over network

---

## 🧪 Testing Your Setup

### 1. Verify Connectivity

```bash
# From any system to System 2
telnet 192.168.1.20 9092

# From any system to System 4
showmount -e 192.168.1.40
```

### 2. End-to-End Test

1. **System 1** (Producer): `create news_alert`
2. **System 4** (Admin): Approve `news_alert`
3. **System 3** (Consumer): `subscribe news_alert`
4. **System 1** (Producer): `send news_alert Breaking news!`
5. **System 3** (Consumer): See message appear! 📨

### 3. Monitor via Web UI

Visit: `http://192.168.1.40:5000`
- See all topics and statuses
- View subscriptions
- Real-time updates

---

## 🔐 Network Requirements

### Ports to Open:

**System 2 (Kafka Broker):**
```bash
sudo ufw allow 9092/tcp  # Kafka
sudo ufw allow 2181/tcp  # ZooKeeper
```

**System 4 (Admin + DB):**
```bash
sudo ufw allow from 192.168.1.0/24 to any port nfs   # NFS
sudo ufw allow from 192.168.1.0/24 to any port 5000  # Web UI
```

---

## 📊 Startup Order

```
1. System 4: Start NFS + Admin Panel
      ↓
2. System 2: Start ZooKeeper + Kafka
      ↓
3. System 1: Start Producer
      ↓
4. System 3: Start Consumer(s)
      ↓
5. Access Web UI: http://192.168.1.40:5000
```

---

## 🎯 Quick Reference Commands

### Start Components:

```bash
# System 2 - Kafka
sudo systemctl start zookeeper
sudo systemctl start kafka

# System 4 - Admin & Web UI
source venv/bin/activate
cd admin && python3 admin_panel.py  # Terminal 1
cd web && python3 app.py            # Terminal 2

# System 1 - Producer
source venv/bin/activate
cd producer && python3 producer.py

# System 3 - Consumer
source venv/bin/activate
cd consumer && python3 consumer.py 1
```

### Check Status:

```bash
# Kafka (System 2)
sudo systemctl status kafka
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Database mount (System 1 or 3)
df -h | grep shared_db

# NFS exports (System 4)
showmount -e localhost
```

---

## 📞 Troubleshooting

### "Cannot connect to Kafka"
✅ Check: `sudo systemctl status kafka` on System 2  
✅ Test: `telnet <SYSTEM2_IP> 9092`  
✅ Firewall: `sudo ufw status`

### "Cannot mount database"
✅ Check NFS: `sudo systemctl status nfs-kernel-server` on System 4  
✅ Test: `showmount -e <SYSTEM4_IP>`  
✅ Manual mount: `sudo mount <SYSTEM4_IP>:/path /mnt/shared_db`

### "Database locked"
✅ SQLite over NFS can have lock issues  
✅ Consider PostgreSQL for production  
✅ See `DISTRIBUTED_SETUP.md` for PostgreSQL setup

---

## 🌟 Key Features

✅ **Automated Setup** - One script per system  
✅ **Network Ready** - Proper firewall config  
✅ **NFS Database** - Shared SQLite across systems  
✅ **Web Monitoring** - Real-time dashboard  
✅ **Production Ready** - Systemd services for Kafka  
✅ **Well Documented** - Step-by-step guides  
✅ **Tested** - Connectivity checks built-in  

---

## 🎓 What You Learned

This distributed setup demonstrates:
- 🔹 Kafka broker configuration for network access
- 🔹 NFS file sharing for distributed database
- 🔹 Multi-system coordination
- 🔹 Network firewall configuration
- 🔹 Service management with systemd
- 🔹 Distributed application architecture

---

## 📚 Next Steps

1. **Read the Quick Start:**  
   `distributed_configs/QUICKSTART_DISTRIBUTED.md`

2. **Prepare Your Systems:**
   - Get IP addresses
   - Ensure network connectivity
   - Have sudo access ready

3. **Run Setup Scripts:**
   - Start with System 4
   - Then System 2
   - Finally Systems 1 & 3

4. **Test Everything:**
   - Follow the testing section
   - Create a topic
   - Send messages
   - Verify on Web UI

---

## 🚀 All Files Pushed to GitHub!

Everything is committed and pushed:
```
✓ https://github.com/kireeti2510/kafka-dynamic-stream
```

Your colleagues can now:
1. Clone the repo on their systems
2. Run the setup scripts
3. Deploy the distributed system

---

## 💡 Pro Tips

1. **Use consistent IPs** - Static IPs recommended
2. **Test connectivity first** - Before running applications
3. **Check logs** - `sudo journalctl -u kafka -f`
4. **Use Web UI** - Easy monitoring at port 5000
5. **Start System 4 first** - It's the database server

---

## 🎊 You're Ready!

Your distributed Kafka streaming system is ready to deploy across 4 systems!

**Start here:** `distributed_configs/QUICKSTART_DISTRIBUTED.md`

**Questions?** Check the troubleshooting sections in the docs.

**Happy Streaming! 🚀**

