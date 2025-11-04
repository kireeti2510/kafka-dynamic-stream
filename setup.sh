#!/bin/bash

# Kafka Dynamic Stream - Quick Start Script
# This script helps you get started with the project quickly

echo "=================================================="
echo "  Kafka Dynamic Stream - Quick Start"
echo "=================================================="
echo ""

# Check if Kafka is installed
if [ ! -d "/opt/kafka" ]; then
    echo "❌ Error: Kafka not found at /opt/kafka"
    echo "   Please install Apache Kafka first."
    exit 1
fi

echo "✓ Kafka installation found"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python3 admin/db_setup.py

if [ $? -eq 0 ]; then
    echo "✓ Database initialized successfully"
else
    echo "❌ Failed to initialize database"
    exit 1
fi
echo ""

# Validate Kafka environment
echo "🔍 Validating Kafka environment..."
python3 kafka_env_setup.py --skip-admin 2>/dev/null

KAFKA_STATUS=$?
if [ $KAFKA_STATUS -eq 0 ]; then
    echo ""
    echo "✓ Kafka environment validation passed!"
    echo "✓ System is ready to run!"
else
    echo ""
    echo "⚠️  Kafka validation failed (services may not be running yet)"
    echo "   This is normal if Kafka hasn't been started."
    echo "   You'll need to start Kafka before running the application."
fi
echo ""

# Display instructions
echo "=================================================="
echo "  Setup Complete! 🎉"
echo "=================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Start Zookeeper (in a new terminal):"
echo "   cd /opt/kafka"
echo "   bin/zookeeper-server-start.sh config/zookeeper.properties"
echo ""
echo "2️⃣  Start Kafka Broker (in a new terminal):"
echo "   cd /opt/kafka"
echo "   bin/kafka-server-start.sh config/server.properties"
echo ""
echo "3️⃣  Start Admin Panel (in a new terminal):"
echo "   cd $(pwd)"
echo "   python3 admin/admin_panel.py"
echo ""
echo "4️⃣  Start Producer (in a new terminal):"
echo "   cd $(pwd)"
echo "   python3 producer/producer.py"
echo ""
echo "5️⃣  Start Consumer (in a new terminal):"
echo "   cd $(pwd)"
echo "   python3 consumer/consumer.py 1"
echo ""
echo "6️⃣  Start Web UI (optional, in a new terminal):"
echo "   cd $(pwd)"
echo "   python3 web/app.py"
echo "   Then visit: http://localhost:5000"
echo ""
echo "=================================================="
echo "📖 For detailed usage, see README.md"
echo "=================================================="
