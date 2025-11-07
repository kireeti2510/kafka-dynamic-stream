# 🌐 System IP Addresses - Kafka Dynamic Stream

This document lists all system IP addresses in your distributed deployment.

---

## 📊 System Configuration

| System | IP Address | Hostname | Components | Ports |
|--------|------------|----------|------------|-------|
| **Admin System** | `192.168.191.183` | admin-server | MySQL Database, Admin Panel | 3306 |
| **Broker System** | `192.168.191.212` | kafka-broker | ZooKeeper, Kafka Broker, Topic Manager | 2181, 9092 |
| **Producer System** | `192.168.191.169` | producer-node | Producer Application | - |
| **Consumer Systems** | (Various IPs) | consumer-nodes | Consumer Applications | - |

---

## 🔧 Current Configuration

### config.json Settings

```json
{
  "bootstrap_servers": "192.168.191.212:9092",
  "mysql": {
    "host": "192.168.191.183",
    "port": 3306,
    "database": "kafka_stream",
    "user": "kafka_user",
    "password": "kafka_password"
  }
}
```

---

## 🏗️ Network Architecture

```
┌─────────────────────────────────────┐
│  Admin System                       │
│  IP: 192.168.191.183               │
│  ┌───────────────────────────────┐ │
│  │ MySQL Server (port 3306)      │ │ ← All systems connect here
│  └───────────────────────────────┘ │
│  ┌───────────────────────────────┐ │
│  │ Admin Panel                   │ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
              ↑
              │ MySQL Connection
              │
┌─────────────┼─────────────────────────┐
│             │                         │
│  ┌──────────┴────────────┐            │
│  │  Broker System        │            │
│  │  IP: 192.168.191.212  │            │
│  │  ┌─────────────────┐  │            │
│  │  │ ZooKeeper       │  │            │
│  │  │ (port 2181)     │  │            │
│  │  └─────────────────┘  │            │
│  │  ┌─────────────────┐  │            │
│  │  │ Kafka Broker    │◄─┼────────────┼─── Producers/Consumers
│  │  │ (port 9092)     │  │            │    connect here
│  │  └─────────────────┘  │            │
│  │  ┌─────────────────┐  │            │
│  │  │ Topic Manager   │  │            │
│  │  └─────────────────┘  │            │
│  └───────────────────────┘            │
│                                       │
│  ┌───────────────────────────────┐   │
│  │  Producer System              │   │
│  │  IP: 192.168.191.169         │   │
│  │  ┌─────────────────────────┐ │   │
│  │  │ Producer Application    │ │   │
│  │  └─────────────────────────┘ │   │
│  └───────────────────────────────┘   │
│                                       │
│  ┌───────────────────────────────┐   │
│  │  Consumer Systems             │   │
│  │  IP: (Various)               │   │
│  │  ┌─────────────────────────┐ │   │
│  │  │ Consumer Applications   │ │   │
│  │  └─────────────────────────┘ │   │
│  └───────────────────────────────┘   │
└───────────────────────────────────────┘
```

---

## 📋 Component Details

### 1. Admin System (192.168.191.183)

**Components:**
- ✅ MySQL Server
- ✅ Admin Panel

**Firewall Rules:**
```bash
sudo ufw allow from 192.168.191.0/24 to any port 3306
sudo ufw enable
```

**Commands:**
```bash
# Start MySQL
sudo systemctl start mysql

# Start Admin Panel
cd kafka-dynamic-stream
python3 admin/admin_panel.py
```

---

### 2. Broker System (192.168.191.212)

**Components:**
- ✅ ZooKeeper (port 2181)
- ✅ Kafka Broker (port 9092)
- ✅ Topic Manager

**Kafka Configuration (`/opt/kafka/config/server.properties`):**
```properties
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://192.168.191.212:9092
zookeeper.connect=localhost:2181
```

**Firewall Rules:**
```bash
sudo ufw allow 9092
sudo ufw allow 2181
sudo ufw enable
```

**Commands:**
```bash
# Terminal 1 - ZooKeeper
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties

# Terminal 2 - Kafka Broker
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties

# Terminal 3 - Topic Manager
cd kafka-dynamic-stream
python3 broker/topic_manager.py
```

---

### 3. Producer System (192.168.191.169)

**Components:**
- ✅ Producer Application

**Requirements:**
- Network access to Broker (192.168.191.212:9092)
- Network access to MySQL (192.168.191.183:3306)
- config.json with correct IPs

**Commands:**
```bash
cd kafka-dynamic-stream
python3 producer/producer.py
```

**Producer Commands:**
```
> create <topic_name>
> send <topic_name> <message>
> list
> active
> quit
```

---

### 4. Consumer Systems (Various IPs)

**Components:**
- ✅ Consumer Applications

**Requirements:**
- Network access to Broker (192.168.191.212:9092)
- Network access to MySQL (192.168.191.183:3306)
- config.json with correct IPs

**Commands:**
```bash
cd kafka-dynamic-stream
python3 consumer/consumer.py 1  # User ID 1
python3 consumer/consumer.py 2  # User ID 2
```

**Consumer Commands:**
```
> list
> subscribe <topic_name>
> subscribed
> unsubscribe <topic_name>
> quit
```

---

## 🔐 Security Configuration

### MySQL Access (192.168.191.183)

```sql
-- Allow access from specific IPs
CREATE USER 'kafka_user'@'192.168.191.212' IDENTIFIED BY 'kafka_password';
CREATE USER 'kafka_user'@'192.168.191.169' IDENTIFIED BY 'kafka_password';
CREATE USER 'kafka_user'@'192.168.191.%' IDENTIFIED BY 'kafka_password';

GRANT ALL PRIVILEGES ON kafka_stream.* TO 'kafka_user'@'192.168.191.%';
FLUSH PRIVILEGES;
```

### Firewall Rules Summary

**Admin System (192.168.191.183):**
```bash
sudo ufw allow from 192.168.191.0/24 to any port 3306
```

**Broker System (192.168.191.212):**
```bash
sudo ufw allow from 192.168.191.0/24 to any port 9092
sudo ufw allow from 192.168.191.0/24 to any port 2181
```

---

## ✅ Verification Commands

### Test MySQL Connection (From Any System)

```bash
# Test from producer (192.168.191.169)
mysql -h 192.168.191.183 -u kafka_user -p
USE kafka_stream;
SHOW TABLES;
EXIT;

# Test from Python
python3 -c "from admin.db_setup import get_connection; conn = get_connection(); print('✓ MySQL Connected'); conn.close()"
```

### Test Kafka Connection (From Any System)

```bash
# Test from producer (192.168.191.169)
/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server 192.168.191.212:9092

# Test from Python
python3 -c "from kafka import KafkaProducer; p = KafkaProducer(bootstrap_servers='192.168.191.212:9092'); print('✓ Kafka Connected'); p.close()"
```

### Test Topic Creation (End-to-End)

```bash
# On Producer (192.168.191.169)
python3 producer/producer.py
> create test_topic

# On Admin (192.168.191.183)
python3 admin/admin_panel.py
# Choose option 2, approve test_topic

# Verify on Broker (192.168.191.212)
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
# Should see: test_topic
```

---

## 📝 Deployment Checklist

### Initial Setup

- [ ] **Admin System (192.168.191.183)**
  - [ ] MySQL installed and running
  - [ ] Database `kafka_stream` created
  - [ ] User `kafka_user` created with remote access
  - [ ] Firewall allows port 3306
  - [ ] Run `python3 admin/db_setup.py` once

- [ ] **Broker System (192.168.191.212)**
  - [ ] Java installed
  - [ ] Kafka installed at `/opt/kafka`
  - [ ] `server.properties` configured with correct IP
  - [ ] Firewall allows ports 9092, 2181
  - [ ] ZooKeeper running
  - [ ] Kafka Broker running
  - [ ] Topic Manager running

- [ ] **Producer System (192.168.191.169)**
  - [ ] Python 3.12+ installed
  - [ ] Dependencies installed (`pip3 install -r requirements.txt`)
  - [ ] config.json has correct IPs
  - [ ] Can connect to MySQL (192.168.191.183:3306)
  - [ ] Can connect to Kafka (192.168.191.212:9092)

- [ ] **Consumer Systems**
  - [ ] Python 3.12+ installed
  - [ ] Dependencies installed
  - [ ] config.json has correct IPs
  - [ ] Can connect to MySQL and Kafka

---

## 🆘 Troubleshooting

### Connection Issues

**Problem:** Producer can't connect to MySQL
```bash
# From producer system (192.168.191.169)
ping 192.168.191.183
telnet 192.168.191.183 3306
```

**Problem:** Producer can't connect to Kafka
```bash
# From producer system (192.168.191.169)
ping 192.168.191.212
telnet 192.168.191.212 9092
```

**Problem:** Firewall blocking
```bash
# On admin system
sudo ufw status
sudo ufw allow from 192.168.191.0/24 to any port 3306

# On broker system
sudo ufw status
sudo ufw allow from 192.168.191.0/24 to any port 9092
```

---

## 📅 Last Updated

**Date:** November 7, 2025  
**Configuration Version:** 3.0  
**Network:** 192.168.191.0/24

---

## 📌 Quick Reference

```
Admin:    192.168.191.183:3306 (MySQL)
Broker:   192.168.191.212:9092 (Kafka)
Producer: 192.168.191.169      (Client)
```

**All systems use the same `config.json` with these connection details!**
