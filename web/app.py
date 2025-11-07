"""
Web UI for Dynamic Kafka Stream
Simple Flask web application to display topics and user subscriptions.

Endpoints:
- GET /              - Home page with all topics
- GET /topics        - JSON API for all topics
- GET /subscriptions - JSON API for all user subscriptions
- GET /active        - JSON API for active topics only

Usage:
    python3 web/app.py
    
    Then visit: http://localhost:5000
"""

import sys
import os
from flask import Flask, render_template_string, jsonify

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import (
    get_all_topics,
    get_topics_by_status,
    get_all_subscriptions,
    initialize_database
)

# Initialize Flask app
app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kafka Dynamic Stream Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        
        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        th {
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }
        
        tr:hover {
            background-color: #f5f5f5;
        }
        
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .status-pending {
            background-color: #ffeaa7;
            color: #d63031;
        }
        
        .status-approved {
            background-color: #74b9ff;
            color: #0984e3;
        }
        
        .status-active {
            background-color: #55efc4;
            color: #00b894;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 15px;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .user-badge {
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 0.9em;
        }
        
        footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Kafka Dynamic Stream Dashboard</h1>
            <p class="subtitle">Real-time Topic and Subscription Management</p>
        </header>
        
        <div class="card">
            <h2>📊 System Statistics</h2>
            <div class="stats" id="stats">
                <div class="stat">
                    <div class="stat-value" id="total-topics">-</div>
                    <div class="stat-label">Total Topics</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="active-topics">-</div>
                    <div class="stat-label">Active Topics</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="pending-topics">-</div>
                    <div class="stat-label">Pending Topics</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="total-subs">-</div>
                    <div class="stat-label">Subscriptions</div>
                </div>
            </div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>📋 Topics</h2>
                <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
                <div id="topics-content">
                    <div class="loading">Loading topics...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>👥 User Subscriptions</h2>
                <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
                <div id="subscriptions-content">
                    <div class="loading">Loading subscriptions...</div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Kafka Dynamic Stream Project | Built with Flask & Kafka</p>
        </footer>
    </div>
    
    <script>
        // Load data on page load
        window.onload = function() {
            loadData();
            // Auto-refresh every 5 seconds
            setInterval(loadData, 5000);
        };
        
        function loadData() {
            loadTopics();
            loadSubscriptions();
        }
        
        function loadTopics() {
            fetch('/topics')
                .then(response => response.json())
                .then(data => {
                    const topicsContent = document.getElementById('topics-content');
                    
                    if (data.topics.length === 0) {
                        topicsContent.innerHTML = '<div class="empty-state">No topics found</div>';
                        return;
                    }
                    
                    let html = '<table><thead><tr><th>Topic Name</th><th>Status</th><th>Created</th></tr></thead><tbody>';
                    
                    data.topics.forEach(topic => {
                        const statusClass = 'status-' + topic.status;
                        const statusIcon = {
                            'pending': '⏳',
                            'approved': '✓',
                            'active': '🟢'
                        }[topic.status] || '•';
                        
                        html += `
                            <tr>
                                <td><strong>${topic.name}</strong></td>
                                <td><span class="status-badge ${statusClass}">${statusIcon} ${topic.status.toUpperCase()}</span></td>
                                <td>${new Date(topic.created_at).toLocaleString()}</td>
                            </tr>
                        `;
                    });
                    
                    html += '</tbody></table>';
                    topicsContent.innerHTML = html;
                    
                    // Update stats
                    updateStats(data);
                })
                .catch(error => {
                    console.error('Error loading topics:', error);
                    document.getElementById('topics-content').innerHTML = 
                        '<div class="empty-state">Error loading topics</div>';
                });
        }
        
        function loadSubscriptions() {
            fetch('/subscriptions')
                .then(response => response.json())
                .then(data => {
                    const subsContent = document.getElementById('subscriptions-content');
                    
                    if (data.subscriptions.length === 0) {
                        subsContent.innerHTML = '<div class="empty-state">No subscriptions found</div>';
                        document.getElementById('total-subs').textContent = '0';
                        return;
                    }
                    
                    let html = '<table><thead><tr><th>User ID</th><th>Topic</th><th>Subscribed At</th></tr></thead><tbody>';
                    
                    data.subscriptions.forEach(sub => {
                        html += `
                            <tr>
                                <td><span class="user-badge">User ${sub.user_id}</span></td>
                                <td><strong>${sub.topic_name}</strong></td>
                                <td>${new Date(sub.subscribed_at).toLocaleString()}</td>
                            </tr>
                        `;
                    });
                    
                    html += '</tbody></table>';
                    subsContent.innerHTML = html;
                    
                    // Update subscription count
                    document.getElementById('total-subs').textContent = data.subscriptions.length;
                })
                .catch(error => {
                    console.error('Error loading subscriptions:', error);
                    document.getElementById('subscriptions-content').innerHTML = 
                        '<div class="empty-state">Error loading subscriptions</div>';
                });
        }
        
        function updateStats(data) {
            document.getElementById('total-topics').textContent = data.topics.length;
            document.getElementById('active-topics').textContent = 
                data.topics.filter(t => t.status === 'active').length;
            document.getElementById('pending-topics').textContent = 
                data.topics.filter(t => t.status === 'pending').length;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/topics')
def get_topics():
    """Get all topics as JSON"""
    try:
        topics = get_all_topics()
        return jsonify({
            'success': True,
            'topics': topics,
            'count': len(topics)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/active')
def get_active_topics():
    """Get active topics as JSON"""
    try:
        topics = get_topics_by_status('active')
        return jsonify({
            'success': True,
            'topics': topics,
            'count': len(topics)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/subscriptions')
def get_subscriptions():
    """Get all subscriptions as JSON"""
    try:
        subscriptions = get_all_subscriptions()
        return jsonify({
            'success': True,
            'subscriptions': subscriptions,
            'count': len(subscriptions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'kafka-dynamic-stream-web'
    })

def main():
    """Main entry point"""
    # Initialize database
    initialize_database()
    
    print("\n" + "="*60)
    print("  KAFKA DYNAMIC STREAM - WEB UI")
    print("="*60)
    print("\n🌐 Starting Flask web server...")
    print("📍 URL: http://localhost:5000")
    print("📍 API Endpoints:")
    print("   - GET /topics        - All topics")
    print("   - GET /active        - Active topics only")
    print("   - GET /subscriptions - User subscriptions")
    print("   - GET /health        - Health check")
    print("\n" + "="*60 + "\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )

if __name__ == '__main__':
    main()
