# 🚀 Distributed Setup - Quick Start Guide

## Overview

This guide will help you deploy Kafka Dynamic Stream across 4 systems on your network.

```
System 1 (Producer)    →  System 2 (Kafka Broker)  →  System 3 (Consumer)
     ↓                                                        ↓
     └──────────────→  System 4 (Admin + Database)  ←────────┘
```

---

## 📋 Prerequisites Checklist

- [ ] 4 systems on the same network
- [ ] All systems can ping each other
- [ ] You know the IP address of each system
- [ ] You have sudo/root access on all systems
- [ ] Systems are running Ubuntu/Debian (or similar)

---

## 🎯 Quick Setup (5 Steps)

### Step 1: Identify Your Systems

Get the IP address on each system:
```bash
hostname -I | awk '{print $1}'
```

**Record your IPs:**
- System 1 (Producer): `__________________`
- System 2 (Kafka Broker): `__________________`
- System 3 (Consumer): `__________________`
- System 4 (Admin + DB): `__________________`

---

### Step 2: Clone Repository on All Systems

**Run on all 4 systems:**
```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream
```

---

### Step 3: Edit Setup Scripts

#### On System 1 (Producer):
```bash
cd ~/kafka-dynamic-stream/distributed_configs
nano setup_system1_producer.sh
```

Edit these lines:
```bash
SYSTEM2_IP="192.168.1.20"      # ← Your System 2 IP
SYSTEM4_IP="192.168.1.40"      # ← Your System 4 IP
SYSTEM4_USER="your_username"   # ← Your username on System 4
```

#### On System 2 (Kafka Broker):
```bash
cd ~/kafka-dynamic-stream/distributed_configs
nano setup_system2_kafka.sh
```

Edit this line:
```bash
SYSTEM2_IP="192.168.1.20"      # ← Your System 2 IP
```

#### On System 3 (Consumer):
```bash
cd ~/kafka-dynamic-stream/distributed_configs
nano setup_system3_consumer.sh
```

Edit these lines:
```bash
SYSTEM2_IP="192.168.1.20"      # ← Your System 2 IP
SYSTEM4_IP="192.168.1.40"      # ← Your System 4 IP
SYSTEM4_USER="your_username"   # ← Your username on System 4
```

#### On System 4 (Admin + Database):
```bash
cd ~/kafka-dynamic-stream/distributed_configs
nano setup_system4_admin.sh
```

Edit these lines:
```bash
SYSTEM4_IP="192.168.1.40"      # ← Your System 4 IP
NETWORK_SUBNET="192.168.1.0/24" # ← Your network subnet
```

---

### Step 4: Run Setup Scripts (IN ORDER!)

#### 4.1 System 4 FIRST (Database Server)
```bash
cd ~/kafka-dynamic-stream/distributed_configs
chmod +x setup_system4_admin.sh
./setup_system4_admin.sh
```

**Wait for it to complete!** ✓

#### 4.2 System 2 (Kafka Broker)
```bash
cd ~/kafka-dynamic-stream/distributed_configs
chmod +x setup_system2_kafka.sh
./setup_system2_kafka.sh
```

**Wait for Kafka to start!** ✓

#### 4.3 System 1 (Producer)
```bash
cd ~/kafka-dynamic-stream/distributed_configs
chmod +x setup_system1_producer.sh
./setup_system1_producer.sh
```

#### 4.4 System 3 (Consumer)
```bash
cd ~/kafka-dynamic-stream/distributed_configs
chmod +x setup_system3_consumer.sh
./setup_system3_consumer.sh
```

---

### Step 5: Start Components

#### System 4 - Start Admin Panel
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd admin
python3 admin_panel.py
```

#### System 4 - Start Web UI (New Terminal)
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd web
python3 app.py
```
Access at: `http://<SYSTEM4_IP>:5000`

#### System 1 - Start Producer
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd producer
python3 producer.py
```

#### System 3 - Start Consumer
```bash
cd ~/kafka-dynamic-stream
source venv/bin/activate
cd consumer
python3 consumer.py 1
```

---

## 🧪 Test the System

### 1. Create a Topic (System 1 - Producer)
```
> create test_topic
```

### 2. Approve Topic (System 4 - Admin Panel)
```
Enter your choice: 2
>> test_topic
```

### 3. Subscribe to Topic (System 3 - Consumer)
```
> subscribe test_topic
```

### 4. Send Message (System 1 - Producer)
```
> send test_topic Hello from distributed system!
```

### 5. See Message (System 3 - Consumer)
```
📨 [test_topic] Message received:
   Content: Hello from distributed system!
```

---

## 🔧 Troubleshooting

### Cannot reach Kafka broker

**Test connectivity:**
```bash
# From System 1 or 3
telnet <SYSTEM2_IP> 9092
```

**If fails:**
```bash
# On System 2 - Check firewall
sudo ufw status
sudo ufw allow 9092/tcp

# Check Kafka is running
sudo systemctl status kafka
```

### Cannot mount shared database

**Test NFS:**
```bash
# On System 4
showmount -e localhost

# On System 1 or 3
showmount -e <SYSTEM4_IP>
```

**If fails:**
```bash
# On System 4 - Check NFS
sudo systemctl status nfs-kernel-server
sudo exportfs -v

# Check firewall
sudo ufw allow from <NETWORK_SUBNET> to any port nfs
```

### Database not accessible

**Check mount:**
```bash
# On System 1 or 3
df -h | grep shared_db
ls -la /mnt/shared_db
```

**Manual mount:**
```bash
sudo mount <SYSTEM4_IP>:/home/<USER>/shared_db /mnt/shared_db
```

---

## 📊 System Status Commands

### System 2 (Kafka Broker)
```bash
# Check Kafka status
sudo systemctl status kafka

# View Kafka logs
sudo journalctl -u kafka -f

# List topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Check if port is open
sudo netstat -tlnp | grep 9092
```

### System 4 (Database Server)
```bash
# Check NFS exports
sudo exportfs -v

# Check who's connected to NFS
sudo netstat -an | grep :2049

# Check database file
ls -la ~/shared_db/topics.db
sqlite3 ~/shared_db/topics.db "SELECT * FROM topics;"
```

### System 1 or 3 (Producer/Consumer)
```bash
# Check NFS mount
df -h | grep shared_db
mount | grep shared_db

# Test Kafka connection
telnet <SYSTEM2_IP> 9092
```

---

## 🎯 Network Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Local Network                       │
│                    (192.168.1.0/24)                         │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────┐        │
│  │ System 1         │         │ System 2         │        │
│  │ Producer         │  Kafka  │ Kafka Broker     │        │
│  │ 192.168.1.10     │◄───────►│ 192.168.1.20     │        │
│  │                  │ :9092   │                  │        │
│  │ • producer.py    │         │ • ZooKeeper:2181 │        │
│  │ • topic_watcher  │         │ • Kafka:9092     │        │
│  │ • input_listener │         │                  │        │
│  └────────┬─────────┘         └──────────────────┘        │
│           │ NFS                                            │
│           │                                                │
│  ┌────────▼─────────┐         ┌──────────────────┐        │
│  │ System 4         │  Kafka  │ System 3         │        │
│  │ Admin + Database │◄───────►│ Consumer         │        │
│  │ 192.168.1.40     │  :9092  │ 192.168.1.30     │        │
│  │                  │         │                  │        │
│  │ • admin_panel.py │         │ • consumer.py    │        │
│  │ • web UI :5000   │         │                  │        │
│  │ • SQLite DB      │         │                  │        │
│  │ • NFS Server     │         │                  │        │
│  └──────────────────┘         └────────┬─────────┘        │
│           ▲                             │                  │
│           │           NFS               │                  │
│           └─────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌟 Success Indicators

✅ System 2: Kafka broker running on port 9092  
✅ System 4: NFS server exporting shared_db  
✅ System 4: Web UI accessible at http://<SYSTEM4_IP>:5000  
✅ System 1: Can connect to Kafka and mount database  
✅ System 3: Can connect to Kafka and mount database  
✅ All systems: Can create topics, approve, and send/receive messages  

---

## 📞 Quick Reference

| Component | System | Port | Command |
|-----------|--------|------|---------|
| ZooKeeper | System 2 | 2181 | `sudo systemctl status zookeeper` |
| Kafka Broker | System 2 | 9092 | `sudo systemctl status kafka` |
| NFS Server | System 4 | 2049 | `sudo systemctl status nfs-kernel-server` |
| Web UI | System 4 | 5000 | Access via browser |
| Producer | System 1 | - | `python3 producer.py` |
| Consumer | System 3 | - | `python3 consumer.py 1` |
| Admin Panel | System 4 | - | `python3 admin_panel.py` |

---

## 💡 Tips

1. **Start System 4 first** - It provides the database all other systems need
2. **Start System 2 second** - It provides Kafka broker for messaging
3. **Test connectivity** before starting applications
4. **Check firewall rules** if components can't communicate
5. **Use Web UI** on System 4 to monitor system status in real-time

---

**Need help? Check logs:**
- Kafka: `sudo journalctl -u kafka -f`
- NFS: `sudo journalctl -u nfs-kernel-server -f`
- Application: Check terminal output

Good luck! 🚀
