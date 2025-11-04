#!/bin/bash

# =============================================================================
# ONE-TIME SETUP SCRIPT
# =============================================================================
# Run this script ONCE before starting the application
# This sets up the Python environment and installs all dependencies
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║         KAFKA DYNAMIC STREAM - ONE-TIME SETUP                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in the correct directory
if [ ! -f "config.json" ]; then
    echo "❌ Error: Please run this script from the kafka_dynamic_stream directory"
    exit 1
fi

echo "📋 Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "   Install: sudo apt install python3"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check Kafka
if [ ! -d "/opt/kafka" ]; then
    echo "❌ Kafka not found at /opt/kafka"
    echo "   Please install Kafka first"
    exit 1
fi
echo "✓ Kafka installation found at /opt/kafka"

# Check Java
if ! command -v java &> /dev/null; then
    echo "❌ Java not found!"
    echo "   Install: sudo apt install default-jdk"
    exit 1
fi
echo "✓ Java found"
echo ""

# Install python3-venv if needed
echo "📦 Checking for python3-venv..."
if ! python3 -m venv --help &> /dev/null; then
    echo "Installing python3-venv..."
    sudo apt install -y python3.12-venv
fi
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
echo "   This may take a minute..."
echo ""

# Uninstall old kafka-python if exists
pip uninstall kafka-python -y &> /dev/null

# Install Flask
pip install Flask==3.0.0 Werkzeug==3.0.1

# Install kafka-python-ng (Python 3.12 compatible)
pip install kafka-python-ng

# Install other dependencies
pip install python-dateutil==2.8.2

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✓ All dependencies installed successfully!"
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python3 admin/db_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to initialize database"
    exit 1
fi

echo ""
echo "✓ Database initialized successfully!"
echo ""

# Make terminal scripts executable
echo "🔧 Making terminal scripts executable..."
chmod +x terminal1_zookeeper.sh
chmod +x terminal2_kafka.sh
chmod +x terminal3_admin.sh
chmod +x terminal4_producer.sh
chmod +x terminal5_consumer.sh
chmod +x terminal6_webui.sh
echo "✓ Terminal scripts are ready"
echo ""

# Deactivate virtual environment
deactivate

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE!                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "Open 6 terminal windows and run these scripts in order:"
echo ""
echo "  1️⃣  Terminal 1:  ./terminal1_zookeeper.sh"
echo "  2️⃣  Terminal 2:  ./terminal2_kafka.sh       (wait 10s after Terminal 1)"
echo "  3️⃣  Terminal 3:  ./terminal3_admin.sh       (wait until Kafka ready)"
echo "  4️⃣  Terminal 4:  ./terminal4_producer.sh    (wait until Kafka ready)"
echo "  5️⃣  Terminal 5:  ./terminal5_consumer.sh    (wait until Kafka ready)"
echo "  6️⃣  Terminal 6:  ./terminal6_webui.sh       (optional)"
echo ""
echo "Or see README.md for detailed instructions"
echo ""
echo "╚═══════════════════════════════════════════════════════════════════════╝"
