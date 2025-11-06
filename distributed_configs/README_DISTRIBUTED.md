# 📡 Distributed Kafka Dynamic Stream - Complete Package

## 📦 What's Included

This directory contains everything you need to deploy Kafka Dynamic Stream across 4 separate systems on your network.

### Files Created:

1. **Setup Scripts** (Ready to run!)
   - `setup_system1_producer.sh` - Producer setup
   - `setup_system2_kafka.sh` - Kafka Broker setup
   - `setup_system3_consumer.sh` - Consumer setup
   - `setup_system4_admin.sh` - Admin + Database setup

2. **Configuration Files**
   - `system1_producer_config.json` - Producer configuration template
   - `system2_kafka_server.properties` - Kafka server configuration
   - `system3_consumer_config.json` - Consumer configuration template
   - `system4_admin_config.json` - Admin configuration template

3. **Documentation**
   - `QUICKSTART_DISTRIBUTED.md` - Quick start guide (START HERE!)
   - `../DISTRIBUTED_SETUP.md` - Detailed setup instructions

4. **Modified Code**
   - `db_setup_distributed.py` - Database module with configurable path

---

## 🚀 Quick Start

### 1. Get Your IP Addresses

On each system:
```bash
hostname -I | awk '{print $1}'
```

### 2. Edit Setup Scripts

Edit each `setup_systemX_*.sh` file and update the IP addresses.

### 3. Run Setup Scripts IN ORDER:

```bash
# System 4 FIRST
./setup_system4_admin.sh

# System 2 SECOND
./setup_system2_kafka.sh

# System 1 and 3 (any order)
./setup_system1_producer.sh
./setup_system3_consumer.sh
```

### 4. Start Components

See `QUICKSTART_DISTRIBUTED.md` for detailed startup commands.

---

## 🌐 System Architecture

```
System 1 (Producer)     →  System 2 (Kafka Broker)  →  System 3 (Consumer)
192.168.1.10               192.168.1.20                192.168.1.30
     ↓                                                       ↓
     └──────────────→   System 4 (Admin + DB)   ←───────────┘
                        192.168.1.40
```

### Ports Used:
- **9092** - Kafka Broker (System 2)
- **2181** - ZooKeeper (System 2)
- **2049** - NFS Server (System 4)
- **5000** - Web UI (System 4)

---

## 📋 System Requirements

### All Systems:
- Ubuntu/Debian Linux
- Python 3.12+
- Network connectivity
- Sudo/root access

### System 2 (Kafka Broker):
- Java 11+
- 2GB+ RAM recommended
- Kafka will be installed at `/opt/kafka`

### System 4 (Admin + DB):
- NFS server capabilities
- Shared directory for database

---

## 🔐 Network Configuration

### Firewall Rules Needed:

**System 2 (Kafka Broker):**
```bash
sudo ufw allow 9092/tcp  # Kafka
sudo ufw allow 2181/tcp  # ZooKeeper
```

**System 4 (Admin + DB):**
```bash
sudo ufw allow from 192.168.1.0/24 to any port nfs  # NFS
sudo ufw allow from 192.168.1.0/24 to any port 5000 # Web UI
```

---

## 📊 What Each System Does

### System 1: Producer
- Runs multi-threaded producer
- Creates topic requests
- Publishes messages to Kafka
- Connects to:
  - Kafka Broker (System 2:9092)
  - Shared Database (System 4 via NFS)

### System 2: Kafka Broker
- Central message hub
- Runs ZooKeeper and Kafka
- Stores messages in topics
- Distributes messages to consumers

### System 3: Consumer
- Runs dynamic consumers
- Subscribes to topics
- Receives messages from Kafka
- Connects to:
  - Kafka Broker (System 2:9092)
  - Shared Database (System 4 via NFS)

### System 4: Admin + Database
- Runs admin panel for approvals
- Hosts shared SQLite database via NFS
- Runs Web UI for monitoring
- Provides database access to all systems

---

## 🧪 Testing Your Setup

### 1. Test Connectivity

From System 1 or 3:
```bash
# Test Kafka
telnet <SYSTEM2_IP> 9092

# Test NFS
showmount -e <SYSTEM4_IP>
```

### 2. Test Database Access

From System 1 or 3:
```bash
ls -la /mnt/shared_db/
```

### 3. Test End-to-End

1. Create topic on System 1
2. Approve on System 4
3. Subscribe on System 3
4. Send message on System 1
5. Receive on System 3

---

## 🔧 Troubleshooting

### Common Issues:

**"Cannot connect to Kafka"**
- Check Kafka is running: `sudo systemctl status kafka`
- Check firewall: `sudo ufw status`
- Verify IP address in config.json

**"Cannot mount NFS"**
- Check NFS server: `sudo systemctl status nfs-kernel-server`
- Verify exports: `sudo exportfs -v`
- Check network connectivity

**"Database locked"**
- SQLite can have issues with concurrent access over NFS
- Consider using PostgreSQL for production

---

## 💡 Best Practices

1. ✅ Always start System 4 first (database server)
2. ✅ Then start System 2 (Kafka broker)
3. ✅ Verify connectivity before starting applications
4. ✅ Use the Web UI to monitor system status
5. ✅ Check logs if something doesn't work

---

## 📞 Quick Commands

### Start Services:
```bash
# System 2 - Kafka
sudo systemctl start zookeeper
sudo systemctl start kafka

# System 4 - NFS
sudo systemctl start nfs-kernel-server

# System 4 - Admin Panel
source venv/bin/activate && cd admin && python3 admin_panel.py

# System 4 - Web UI
source venv/bin/activate && cd web && python3 app.py

# System 1 - Producer
source venv/bin/activate && cd producer && python3 producer.py

# System 3 - Consumer
source venv/bin/activate && cd consumer && python3 consumer.py 1
```

### Check Status:
```bash
# Kafka (System 2)
sudo systemctl status kafka
sudo journalctl -u kafka -f

# NFS (System 4)
sudo systemctl status nfs-kernel-server
showmount -e localhost

# Database (System 4)
sqlite3 ~/shared_db/topics.db "SELECT * FROM topics;"
```

---

## 📚 Additional Resources

- Main README: `../README.md`
- Detailed Setup: `../DISTRIBUTED_SETUP.md`
- Quick Start: `QUICKSTART_DISTRIBUTED.md`
- Configuration Guide: See individual config files

---

## 🎯 Success Checklist

Before starting applications, verify:

- [ ] All 4 systems can ping each other
- [ ] Firewall rules configured
- [ ] Kafka running on System 2
- [ ] NFS server running on System 4
- [ ] Database accessible from Systems 1 & 3
- [ ] IP addresses updated in all config files
- [ ] Dependencies installed on all systems

---

**Ready to deploy? Start with `QUICKSTART_DISTRIBUTED.md`!** 🚀

