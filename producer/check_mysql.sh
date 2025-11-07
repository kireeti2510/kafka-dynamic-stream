#!/bin/bash
# MySQL Connection Test for Producer
# Run this on the Producer system to diagnose MySQL connectivity

echo "============================================================"
echo "🔍 MySQL Connection Test for Producer"
echo "============================================================"
echo ""

# Read config.json to get MySQL settings
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found!"
    echo "   Please run this script from kafka-dynamic-stream directory"
    exit 1
fi

# Extract MySQL host from config
MYSQL_HOST=$(grep -o '"host"[[:space:]]*:[[:space:]]*"[^"]*"' config.json | grep mysql -A 1 | tail -1 | cut -d'"' -f4)
MYSQL_PORT=3306
MYSQL_USER="kafka_user"
MYSQL_PASS="kafka_password"
MYSQL_DB="kafka_stream"

echo "Configuration from config.json:"
echo "  Host:     $MYSQL_HOST"
echo "  Port:     $MYSQL_PORT"
echo "  Database: $MYSQL_DB"
echo "  User:     $MYSQL_USER"
echo ""
echo "============================================================"
echo ""

# Test 1: Network connectivity
echo "[Test 1] Testing network connectivity to MySQL host..."
if ping -c 3 -W 2 "$MYSQL_HOST" > /dev/null 2>&1; then
    echo "✅ Host $MYSQL_HOST is reachable"
else
    echo "❌ Host $MYSQL_HOST is NOT reachable"
    echo "   Cannot ping the MySQL server"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   1. Verify IP address: $MYSQL_HOST"
    echo "   2. Check if systems are on same network"
    echo "   3. Check firewall rules"
    exit 1
fi
echo ""

# Test 2: MySQL port connectivity
echo "[Test 2] Testing MySQL port connectivity..."
if command -v nc > /dev/null 2>&1; then
    if nc -zv -w 3 "$MYSQL_HOST" "$MYSQL_PORT" 2>&1 | grep -q succeeded; then
        echo "✅ Port $MYSQL_PORT is open on $MYSQL_HOST"
    else
        echo "❌ Port $MYSQL_PORT is NOT accessible on $MYSQL_HOST"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   1. Check if MySQL is running: systemctl status mysql"
        echo "   2. Check MySQL bind-address configuration"
        echo "   3. Check firewall: sudo ufw status"
        exit 1
    fi
else
    echo "⚠️  'nc' command not found, skipping port test"
fi
echo ""

# Test 3: MySQL connection
echo "[Test 3] Testing MySQL connection..."
if command -v mysql > /dev/null 2>&1; then
    if mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS" -e "SELECT 1;" > /dev/null 2>&1; then
        echo "✅ MySQL connection successful!"
    else
        echo "❌ MySQL connection FAILED"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   1. Check user grants on MySQL server:"
        echo "      mysql -u root -p -e \"SELECT User, Host FROM mysql.user WHERE User='kafka_user';\""
        echo "   2. Verify password is correct"
        echo "   3. Check MySQL error logs"
        exit 1
    fi
else
    echo "⚠️  'mysql' client not installed, trying Python test..."
    if python3 producer/test_mysql.py; then
        echo "✅ Python MySQL test passed"
    else
        echo "❌ Python MySQL test failed"
        exit 1
    fi
fi
echo ""

# Test 4: Query database
echo "[Test 4] Querying topics table..."
if command -v mysql > /dev/null 2>&1; then
    TOPIC_COUNT=$(mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" -se "SELECT COUNT(*) FROM topics;" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✅ Topics in database: $TOPIC_COUNT"
        
        echo ""
        echo "[Test 5] Listing all topics..."
        mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" -e "SELECT name, status, created_at FROM topics;" 2>/dev/null | while read line; do
            echo "   $line"
        done
    else
        echo "❌ Cannot query topics table"
    fi
fi
echo ""

# Test 6: Multiple connection test
echo "[Test 6] Testing connection stability (10 attempts)..."
SUCCESS=0
FAILED=0
for i in {1..10}; do
    printf "  Attempt %2d: " "$i"
    if mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS" -e "SELECT 1;" > /dev/null 2>&1; then
        echo "✅"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "❌"
        FAILED=$((FAILED + 1))
    fi
    sleep 0.3
done
echo ""
echo "Results: $SUCCESS success, $FAILED failed"

if [ $FAILED -gt 0 ]; then
    echo "⚠️  Network instability detected! ($FAILED failures)"
    echo ""
    echo "🔧 Possible causes:"
    echo "   - Intermittent network issues"
    echo "   - Firewall dropping packets"
    echo "   - MySQL max_connections limit reached"
    echo "   - WiFi instability (use wired connection)"
else
    echo "✅ All connections stable!"
fi
echo ""

echo "============================================================"
echo "✅ MySQL diagnostic complete!"
echo "============================================================"
echo ""
echo "📋 Summary:"
echo "   MySQL Host: $MYSQL_HOST:$MYSQL_PORT"
echo "   Network: $([ $FAILED -eq 0 ] && echo "Stable ✅" || echo "Unstable ⚠️")"
echo "   Status: $([ $FAILED -eq 0 ] && echo "Ready for production" || echo "Needs attention")"
echo ""
