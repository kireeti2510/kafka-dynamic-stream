# 🌐 Distributed Kafka Dynamic Stream Setup

## Network Architecture

This guide helps you deploy the Kafka Dynamic Stream across 4 systems on the same network.

```
┌─────────────────────────────────────────────────────────────────┐
│                      Network: 192.168.1.x/24                    │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ System 1     │  │ System 2     │  │ System 3     │         │
│  │ Producer     │→→│ Kafka Broker │→→│ Consumer     │         │
│  │ 192.168.1.10 │  │ 192.168.1.20 │  │ 192.168.1.30 │         │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘         │
│         │                                    │                 │
│         └────────────────┬───────────────────┘                 │
│                          ↓                                     │
│                  ┌──────────────┐                              │
│                  │ System 4     │                              │
│                  │ Admin + DB   │                              │
│                  │ 192.168.1.40 │                              │
│                  └──────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### Network Requirements
- All 4 systems on same network (e.g., 192.168.1.x/24)
- Open ports:
  - **Kafka Broker (System 2):** 9092 (Kafka), 2181 (ZooKeeper)
  - **Admin Server (System 4):** 5000 (Web UI - optional), 3306 or custom (DB access)
- Systems can ping each other

### Software Requirements (All Systems)
- Python 3.12+
- Git
- Network connectivity

### System-Specific Requirements
- **System 2 (Kafka Broker):** Java 11+, Apache Kafka installed

---

## 🔧 System Configuration

### **Get IP Addresses First**

On each system, find the IP address:
```bash
# On Linux
ip addr show | grep inet

# OR
hostname -I
```

**Example IPs (replace with your actual IPs):**
- System 1 (Producer): `192.168.1.10`
- System 2 (Kafka Broker): `192.168.1.20`
- System 3 (Consumer): `192.168.1.30`
- System 4 (Admin + DB): `192.168.1.40`

---

## 📦 System 1: Producer

### **Setup Steps**

1. **Clone Repository**
```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream
```

2. **Install Dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install kafka-python-ng python-dateutil
```

3. **Create Configuration** (`config_producer.json`)
```bash
cat > config_producer.json << 'EOF'
{
  "bootstrap_servers": "192.168.1.20:9092",
  "db_server": "192.168.1.40",
  "db_port": 5432,
  "default_partitions": 3,
  "default_replication_factor": 1,
  "topic_watcher_poll_interval": 5,
  "acks": 1,
  "compression_type": "gzip",
  "retries": 3,
  "auto_offset_reset": "latest"
}
EOF
```

4. **Update Producer Code** (modify to use remote DB)
```bash
# We'll create modified files for this
```

5. **Run Producer**
```bash
source venv/bin/activate
cd producer
python3 producer.py
```

---

## ⚙️ System 2: Kafka Broker (Central Hub)

### **Setup Steps**

1. **Install Java**
```bash
sudo apt update
sudo apt install -y openjdk-11-jdk
java -version
```

2. **Install Kafka**
```bash
cd /opt
sudo wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz
sudo tar -xzf kafka_2.13-3.6.0.tgz
sudo mv kafka_2.13-3.6.0 kafka
```

3. **Configure Kafka for Network Access**

Edit `/opt/kafka/config/server.properties`:
```bash
sudo nano /opt/kafka/config/server.properties
```

**Key Changes:**
```properties
# CHANGE THIS - Set to your System 2 IP
listeners=PLAINTEXT://192.168.1.20:9092

# CHANGE THIS - Advertised listeners
advertised.listeners=PLAINTEXT://192.168.1.20:9092

# Network settings
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Disable auto topic creation
auto.create.topics.enable=false

# Log settings
log.dirs=/tmp/kafka-logs
num.partitions=3
log.retention.hours=168
```

4. **Configure ZooKeeper for Network Access**

Edit `/opt/kafka/config/zookeeper.properties`:
```bash
sudo nano /opt/kafka/config/zookeeper.properties
```

**Key Changes:**
```properties
# Data directory
dataDir=/tmp/zookeeper

# Client port
clientPort=2181

# Max client connections
maxClientCnxns=0

# Admin server (optional)
admin.enableServer=false
```

5. **Configure Firewall**
```bash
# Allow Kafka and ZooKeeper ports
sudo ufw allow 9092/tcp
sudo ufw allow 2181/tcp
sudo ufw enable
```

6. **Start Services**

Terminal 1 - ZooKeeper:
```bash
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
```

Terminal 2 - Kafka Broker:
```bash
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties
```

7. **Verify Kafka is Accessible**
```bash
# From System 2 (local test)
/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# From another system (e.g., System 1)
telnet 192.168.1.20 9092
```

---

## 📊 System 3: Consumer

### **Setup Steps**

1. **Clone Repository**
```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream
```

2. **Install Dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install kafka-python-ng python-dateutil
```

3. **Create Configuration** (`config_consumer.json`)
```bash
cat > config_consumer.json << 'EOF'
{
  "bootstrap_servers": "192.168.1.20:9092",
  "db_server": "192.168.1.40",
  "db_port": 5432,
  "auto_offset_reset": "latest"
}
EOF
```

4. **Run Consumer**
```bash
source venv/bin/activate
cd consumer
python3 consumer.py 1  # User ID 1
```

Multiple consumers on same system:
```bash
# Terminal 1
python3 consumer.py 1

# Terminal 2
python3 consumer.py 2
```

---

## 🗄️ System 4: Admin + SQLite Database

### **Option A: Shared SQLite (File-Based - Simple)**

**Note:** SQLite is file-based and not ideal for network access. We'll use a shared network directory.

1. **Clone Repository**
```bash
cd ~
git clone https://github.com/kireeti2510/kafka-dynamic-stream.git
cd kafka-dynamic-stream
```

2. **Install Dependencies**
```bash
python3 -m venv venv
source venv/bin/activate
pip install kafka-python-ng Flask python-dateutil
```

3. **Setup Shared Database Directory**
```bash
# Create shared directory
mkdir -p ~/shared_db

# Install NFS Server
sudo apt update
sudo apt install -y nfs-kernel-server

# Configure NFS export
sudo nano /etc/exports
```

Add this line:
```
/home/YOUR_USERNAME/shared_db 192.168.1.0/24(rw,sync,no_subtree_check)
```

```bash
# Apply changes
sudo exportfs -ra
sudo systemctl restart nfs-kernel-server

# Configure firewall
sudo ufw allow from 192.168.1.0/24 to any port nfs
```

4. **Run Admin Panel**
```bash
source venv/bin/activate
cd admin
python3 admin_panel.py
```

5. **Run Web UI**
```bash
source venv/bin/activate
cd web
python3 app.py
# Access at: http://192.168.1.40:5000
```

---

### **Option B: PostgreSQL (Network Database - Recommended)**

For true distributed setup, use PostgreSQL instead of SQLite.

1. **Install PostgreSQL on System 4**
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
```

2. **Configure PostgreSQL for Network Access**
```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Change:
```
listen_addresses = '*'
```

Edit pg_hba.conf:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Add:
```
host    all    all    192.168.1.0/24    md5
```

3. **Restart PostgreSQL**
```bash
sudo systemctl restart postgresql
```

4. **Create Database**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE kafka_stream;
CREATE USER kafka_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE kafka_stream TO kafka_user;
\q
```

5. **Install psycopg2 on All Systems**
```bash
pip install psycopg2-binary
```

---

## 🔐 Network Setup on Other Systems

### **System 1 (Producer) - Mount Shared DB**

```bash
# Install NFS client
sudo apt install -y nfs-common

# Create mount point
sudo mkdir -p /mnt/shared_db

# Mount shared directory
sudo mount 192.168.1.40:/home/YOUR_USERNAME/shared_db /mnt/shared_db

# Auto-mount on boot (optional)
echo "192.168.1.40:/home/YOUR_USERNAME/shared_db /mnt/shared_db nfs defaults 0 0" | sudo tee -a /etc/fstab
```

### **System 3 (Consumer) - Mount Shared DB**

Same as System 1.

---

## 📝 Modified Configuration Files

I'll create modified versions of the code to work with distributed setup...

