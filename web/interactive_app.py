"""
Interactive Web UI for Kafka Dynamic Stream
Enhanced Flask application with admin, producer, and consumer interfaces.

Features:
- Admin: Approve/reject/deactivate topics via web UI
- Producer: Create topics and send messages via web UI
- Consumer: Subscribe to topics and view messages in real-time via web UI
- Retains all existing terminal functionality

Usage:
    python3 web/interactive_app.py
    
    Then visit: http://localhost:8080
"""

import sys
import os
import json
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request, session
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError
import threading
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from admin.db_setup import (
    get_all_topics,
    get_topics_by_status,
    get_all_subscriptions,
    initialize_database,
    update_topic_status,
    add_topic,
    subscribe_user_to_topic,
    unsubscribe_user_from_topic,
    get_user_subscriptions,
    load_db_config
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'kafka-dynamic-stream-secret-key-2024'

# Load configuration
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()

# HTML Template for Interactive UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kafka Dynamic Stream - Interactive Dashboard</title>
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
            max-width: 1400px;
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
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab-button {
            flex: 1;
            padding: 15px 30px;
            background: white;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .tab-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .tab-button.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: bold;
        }
        
        input[type="text"],
        input[type="number"],
        textarea,
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-right: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-warning {
            background: #ffc107;
            color: #333;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .topic-list {
            display: grid;
            gap: 15px;
        }
        
        .topic-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .topic-info {
            flex: 1;
        }
        
        .topic-name {
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .topic-meta {
            color: #666;
            font-size: 0.9em;
        }
        
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-pending {
            background: #ffc107;
            color: #333;
        }
        
        .status-active {
            background: #28a745;
            color: white;
        }
        
        .status-rejected {
            background: #dc3545;
            color: white;
        }
        
        .status-deactivated {
            background: #6c757d;
            color: white;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
        }
        
        .message-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        
        .message-topic {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .message-content {
            color: #333;
            margin-bottom: 5px;
        }
        
        .message-time {
            color: #666;
            font-size: 0.85em;
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .alert-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .alert-info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        
        .messages-container {
            max-height: 400px;
            overflow-y: auto;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        
        .subscription-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .subscription-item {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .unsubscribe-btn {
            background: rgba(255, 255, 255, 0.3);
            border: none;
            color: white;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            cursor: pointer;
            font-weight: bold;
        }
        
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Kafka Dynamic Stream</h1>
            <p class="subtitle">Interactive Dashboard - Admin, Producer & Consumer</p>
        </header>
        
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('admin')">👨‍💼 Admin Panel</button>
            <button class="tab-button" onclick="showTab('producer')">📤 Producer</button>
            <button class="tab-button" onclick="showTab('consumer')">📥 Consumer</button>
            <button class="tab-button" onclick="showTab('dashboard')">📊 Dashboard</button>
        </div>
        
        <!-- Admin Tab -->
        <div id="admin-tab" class="tab-content active">
            <div class="card">
                <h2>Pending Topic Approvals</h2>
                <div id="pending-topics" class="topic-list"></div>
            </div>
            
            <div class="card">
                <h2>All Topics</h2>
                <div id="all-topics" class="topic-list"></div>
            </div>
        </div>
        
        <!-- Producer Tab -->
        <div id="producer-tab" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h2>Create New Topic</h2>
                    <div class="form-group">
                        <label for="producer-id">Producer ID:</label>
                        <input type="number" id="producer-id" placeholder="Enter your producer ID (e.g., 1)" value="1">
                    </div>
                    <div class="form-group">
                        <label for="topic-name">Topic Name:</label>
                        <input type="text" id="topic-name" placeholder="Enter topic name">
                    </div>
                    <button class="btn btn-primary" onclick="createTopic()">Create Topic Request</button>
                    <div id="create-result" style="margin-top: 15px;"></div>
                </div>
                
                <div class="card">
                    <h2>Send Message</h2>
                    <div class="form-group">
                        <label for="send-topic">Select Topic:</label>
                        <select id="send-topic"></select>
                    </div>
                    <div class="form-group">
                        <label for="message-content">Message:</label>
                        <textarea id="message-content" placeholder="Enter your message here"></textarea>
                    </div>
                    <button class="btn btn-success" onclick="sendMessage()">Send Message</button>
                    <div id="send-result" style="margin-top: 15px;"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>My Topic Requests</h2>
                <div id="producer-topics" class="topic-list"></div>
            </div>
        </div>
        
        <!-- Consumer Tab -->
        <div id="consumer-tab" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h2>Subscribe to Topics</h2>
                    <div class="form-group">
                        <label for="consumer-id">Consumer ID:</label>
                        <input type="number" id="consumer-id" placeholder="Enter your consumer ID (e.g., 1)" value="1">
                    </div>
                    <div class="form-group">
                        <label for="subscribe-topic">Select Topic:</label>
                        <select id="subscribe-topic"></select>
                    </div>
                    <button class="btn btn-primary" onclick="subscribeTopic()">Subscribe</button>
                    <div id="subscribe-result" style="margin-top: 15px;"></div>
                </div>
                
                <div class="card">
                    <h2>My Subscriptions</h2>
                    <div id="my-subscriptions" class="subscription-list"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>Received Messages</h2>
                <div id="consumer-messages" class="messages-container">
                    <p style="text-align: center; color: #666;">Messages will appear here when received...</p>
                </div>
            </div>
        </div>
        
        <!-- Dashboard Tab -->
        <div id="dashboard-tab" class="tab-content">
            <div class="grid-2">
                <div class="card">
                    <h2>System Statistics</h2>
                    <div id="system-stats"></div>
                </div>
                
                <div class="card">
                    <h2>Active Topics</h2>
                    <div id="active-topics" class="topic-list"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>All Subscriptions</h2>
                <div id="all-subscriptions"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentTab = 'admin';
        let currentProducerId = 1;
        let currentConsumerId = 1;
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            currentTab = tabName;
            
            // Load data for the tab
            loadTabData(tabName);
        }
        
        function loadTabData(tabName) {
            if (tabName === 'admin') {
                loadPendingTopics();
                loadAllTopics();
            } else if (tabName === 'producer') {
                loadActiveTopicsForProducer();
                loadProducerTopics();
            } else if (tabName === 'consumer') {
                loadActiveTopicsForConsumer();
                loadMySubscriptions();
                loadConsumerMessages();
            } else if (tabName === 'dashboard') {
                loadSystemStats();
                loadActiveTopicsDashboard();
                loadAllSubscriptions();
            }
        }
        
        // Admin Functions
        async function loadPendingTopics() {
            const response = await fetch('/api/topics/pending');
            const topics = await response.json();
            const container = document.getElementById('pending-topics');
            
            if (topics.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No pending topics</p>';
                return;
            }
            
            container.innerHTML = topics.map(topic => `
                <div class="topic-item">
                    <div class="topic-info">
                        <div class="topic-name">${topic.topic_name}</div>
                        <div class="topic-meta">Created: ${topic.created_at}</div>
                    </div>
                    <div class="action-buttons">
                        <button class="btn btn-success" onclick="approveTopic('${topic.topic_name}')">✓ Approve</button>
                        <button class="btn btn-danger" onclick="rejectTopic('${topic.topic_name}')">✗ Reject</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function loadAllTopics() {
            const response = await fetch('/api/topics/all');
            const topics = await response.json();
            const container = document.getElementById('all-topics');
            
            container.innerHTML = topics.map(topic => {
                let statusClass = 'status-' + topic.status;
                let actions = '';
                
                if (topic.status === 'active') {
                    actions = `<button class="btn btn-warning" onclick="deactivateTopic('${topic.topic_name}')">Deactivate</button>`;
                }
                
                return `
                    <div class="topic-item">
                        <div class="topic-info">
                            <div class="topic-name">${topic.topic_name}</div>
                            <div class="topic-meta">Status: <span class="status-badge ${statusClass}">${topic.status}</span></div>
                        </div>
                        <div class="action-buttons">
                            ${actions}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        async function approveTopic(topicName) {
            const response = await fetch('/api/admin/approve', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({topic_name: topicName})
            });
            const result = await response.json();
            alert(result.message);
            loadPendingTopics();
            loadAllTopics();
        }
        
        async function rejectTopic(topicName) {
            const response = await fetch('/api/admin/reject', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({topic_name: topicName})
            });
            const result = await response.json();
            alert(result.message);
            loadPendingTopics();
            loadAllTopics();
        }
        
        async function deactivateTopic(topicName) {
            if (!confirm('Are you sure you want to deactivate this topic?')) return;
            
            const response = await fetch('/api/admin/deactivate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({topic_name: topicName})
            });
            const result = await response.json();
            alert(result.message);
            loadAllTopics();
        }
        
        // Producer Functions
        async function loadActiveTopicsForProducer() {
            const response = await fetch('/api/topics/active');
            const topics = await response.json();
            const select = document.getElementById('send-topic');
            
            select.innerHTML = '<option value="">Select a topic</option>' + 
                topics.map(topic => `<option value="${topic.topic_name}">${topic.topic_name}</option>`).join('');
        }
        
        async function loadProducerTopics() {
            const producerId = document.getElementById('producer-id').value;
            const response = await fetch(`/api/producer/topics/${producerId}`);
            const topics = await response.json();
            const container = document.getElementById('producer-topics');
            
            if (topics.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No topic requests yet</p>';
                return;
            }
            
            container.innerHTML = topics.map(topic => {
                let statusClass = 'status-' + topic.status;
                return `
                    <div class="topic-item">
                        <div class="topic-info">
                            <div class="topic-name">${topic.topic_name}</div>
                            <div class="topic-meta">Status: <span class="status-badge ${statusClass}">${topic.status}</span> | Created: ${topic.created_at}</div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        async function createTopic() {
            const producerId = document.getElementById('producer-id').value;
            const topicName = document.getElementById('topic-name').value;
            const resultDiv = document.getElementById('create-result');
            
            if (!topicName) {
                resultDiv.innerHTML = '<div class="alert alert-error">Please enter a topic name</div>';
                return;
            }
            
            const response = await fetch('/api/producer/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({producer_id: parseInt(producerId), topic_name: topicName})
            });
            const result = await response.json();
            
            if (result.success) {
                resultDiv.innerHTML = '<div class="alert alert-success">' + result.message + '</div>';
                document.getElementById('topic-name').value = '';
                loadProducerTopics();
            } else {
                resultDiv.innerHTML = '<div class="alert alert-error">' + result.message + '</div>';
            }
        }
        
        async function sendMessage() {
            const topicName = document.getElementById('send-topic').value;
            const message = document.getElementById('message-content').value;
            const producerId = document.getElementById('producer-id').value;
            const resultDiv = document.getElementById('send-result');
            
            if (!topicName || !message) {
                resultDiv.innerHTML = '<div class="alert alert-error">Please select a topic and enter a message</div>';
                return;
            }
            
            const response = await fetch('/api/producer/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    producer_id: parseInt(producerId),
                    topic_name: topicName,
                    message: message
                })
            });
            const result = await response.json();
            
            if (result.success) {
                resultDiv.innerHTML = '<div class="alert alert-success">' + result.message + '</div>';
                document.getElementById('message-content').value = '';
            } else {
                resultDiv.innerHTML = '<div class="alert alert-error">' + result.message + '</div>';
            }
        }
        
        // Consumer Functions
        async function loadActiveTopicsForConsumer() {
            const response = await fetch('/api/topics/active');
            const topics = await response.json();
            const select = document.getElementById('subscribe-topic');
            
            select.innerHTML = '<option value="">Select a topic</option>' + 
                topics.map(topic => `<option value="${topic.topic_name}">${topic.topic_name}</option>`).join('');
        }
        
        async function loadMySubscriptions() {
            const consumerId = document.getElementById('consumer-id').value;
            const response = await fetch(`/api/consumer/subscriptions/${consumerId}`);
            const subscriptions = await response.json();
            const container = document.getElementById('my-subscriptions');
            
            if (subscriptions.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No subscriptions yet</p>';
                return;
            }
            
            container.innerHTML = subscriptions.map(sub => `
                <div class="subscription-item">
                    ${sub.topic_name}
                    <button class="unsubscribe-btn" onclick="unsubscribeTopic('${sub.topic_name}')">×</button>
                </div>
            `).join('');
        }
        
        async function subscribeTopic() {
            const consumerId = document.getElementById('consumer-id').value;
            const topicName = document.getElementById('subscribe-topic').value;
            const resultDiv = document.getElementById('subscribe-result');
            
            if (!topicName) {
                resultDiv.innerHTML = '<div class="alert alert-error">Please select a topic</div>';
                return;
            }
            
            const response = await fetch('/api/consumer/subscribe', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    consumer_id: parseInt(consumerId),
                    topic_name: topicName
                })
            });
            const result = await response.json();
            
            if (result.success) {
                resultDiv.innerHTML = '<div class="alert alert-success">' + result.message + '</div>';
                loadMySubscriptions();
            } else {
                resultDiv.innerHTML = '<div class="alert alert-error">' + result.message + '</div>';
            }
        }
        
        async function unsubscribeTopic(topicName) {
            const consumerId = document.getElementById('consumer-id').value;
            
            const response = await fetch('/api/consumer/unsubscribe', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    consumer_id: parseInt(consumerId),
                    topic_name: topicName
                })
            });
            const result = await response.json();
            alert(result.message);
            loadMySubscriptions();
        }
        
        async function loadConsumerMessages() {
            const consumerId = document.getElementById('consumer-id').value;
            const response = await fetch(`/api/consumer/messages/${consumerId}`);
            const messages = await response.json();
            const container = document.getElementById('consumer-messages');
            
            if (messages.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No messages received yet. Subscribe to topics to receive messages.</p>';
                return;
            }
            
            container.innerHTML = messages.map(msg => `
                <div class="message-box">
                    <div class="message-topic">[${msg.topic}]</div>
                    <div class="message-content">${msg.message}</div>
                    <div class="message-time">${msg.timestamp}</div>
                </div>
            `).join('');
        }
        
        // Dashboard Functions
        async function loadSystemStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            const container = document.getElementById('system-stats');
            
            container.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                    <div style="text-align: center; padding: 20px; background: #667eea; color: white; border-radius: 8px;">
                        <div style="font-size: 3em; font-weight: bold;">${stats.total_topics}</div>
                        <div>Total Topics</div>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #28a745; color: white; border-radius: 8px;">
                        <div style="font-size: 3em; font-weight: bold;">${stats.active_topics}</div>
                        <div>Active Topics</div>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #ffc107; color: #333; border-radius: 8px;">
                        <div style="font-size: 3em; font-weight: bold;">${stats.pending_topics}</div>
                        <div>Pending Topics</div>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #764ba2; color: white; border-radius: 8px;">
                        <div style="font-size: 3em; font-weight: bold;">${stats.total_subscriptions}</div>
                        <div>Total Subscriptions</div>
                    </div>
                </div>
            `;
        }
        
        async function loadActiveTopicsDashboard() {
            const response = await fetch('/api/topics/active');
            const topics = await response.json();
            const container = document.getElementById('active-topics');
            
            if (topics.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No active topics</p>';
                return;
            }
            
            container.innerHTML = topics.map(topic => `
                <div class="topic-item">
                    <div class="topic-info">
                        <div class="topic-name">${topic.topic_name}</div>
                        <div class="topic-meta">Created: ${topic.created_at}</div>
                    </div>
                </div>
            `).join('');
        }
        
        async function loadAllSubscriptions() {
            const response = await fetch('/api/subscriptions');
            const subscriptions = await response.json();
            const container = document.getElementById('all-subscriptions');
            
            if (subscriptions.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No subscriptions</p>';
                return;
            }
            
            container.innerHTML = '<div class="topic-list">' + subscriptions.map(sub => `
                <div class="topic-item">
                    <div class="topic-info">
                        <div class="topic-name">Consumer ${sub.consumer_id} → ${sub.topic_name}</div>
                        <div class="topic-meta">Status: ${sub.status} | Subscribed: ${sub.subscribed_at}</div>
                    </div>
                </div>
            `).join('') + '</div>';
        }
        
        // Auto-refresh
        setInterval(() => {
            loadTabData(currentTab);
        }, 5000);
        
        // Initial load
        loadTabData('admin');
    </script>
</body>
</html>
"""

# API Routes

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)

# Backwards compatibility routes (without /api/ prefix)
@app.route('/topics')
def get_topics_compat():
    """Get all topics (backwards compatibility)"""
    topics = get_all_topics()
    return jsonify([{
        'topic_name': t['name'],
        'status': t['status'],
        'created_at': str(t['created_at'])
    } for t in topics])

@app.route('/subscriptions')
def get_subscriptions_compat():
    """Get all subscriptions (backwards compatibility)"""
    subs = get_all_subscriptions()
    return jsonify([{
        'consumer_id': s['user_id'],
        'topic_name': s['topic_name'],
        'status': s['status'],
        'subscribed_at': str(s['subscribed_at'])
    } for s in subs])

@app.route('/api/topics/all')
def get_all_topics_api():
    """Get all topics"""
    topics = get_all_topics()
    return jsonify([{
        'topic_name': t['name'],
        'status': t['status'],
        'created_at': str(t['created_at'])
    } for t in topics])

@app.route('/api/topics/pending')
def get_pending_topics():
    """Get pending topics"""
    topics = get_topics_by_status('pending')
    return jsonify([{
        'topic_name': t['name'],
        'status': t['status'],
        'created_at': str(t['created_at'])
    } for t in topics])

@app.route('/api/topics/active')
def get_active_topics():
    """Get active topics"""
    topics = get_topics_by_status('active')
    return jsonify([{
        'topic_name': t['name'],
        'status': t['status'],
        'created_at': str(t['created_at'])
    } for t in topics])

@app.route('/api/subscriptions')
def get_subscriptions():
    """Get all subscriptions"""
    subs = get_all_subscriptions()
    return jsonify([{
        'consumer_id': s['user_id'],
        'topic_name': s['topic_name'],
        'status': s['status'],
        'subscribed_at': str(s['subscribed_at'])
    } for s in subs])

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    all_topics = get_all_topics()
    active_topics = get_topics_by_status('active')
    pending_topics = get_topics_by_status('pending')
    subscriptions = get_all_subscriptions()
    
    return jsonify({
        'total_topics': len(all_topics),
        'active_topics': len(active_topics),
        'pending_topics': len(pending_topics),
        'total_subscriptions': len(subscriptions)
    })

# Admin API Routes

@app.route('/api/admin/approve', methods=['POST'])
def approve_topic():
    """Approve a pending topic"""
    data = request.json
    topic_name = data.get('topic_name')
    
    try:
        update_topic_status(topic_name, 'active')
        return jsonify({'success': True, 'message': f'Topic {topic_name} approved successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/reject', methods=['POST'])
def reject_topic():
    """Reject a pending topic"""
    data = request.json
    topic_name = data.get('topic_name')
    
    try:
        update_topic_status(topic_name, 'rejected')
        return jsonify({'success': True, 'message': f'Topic {topic_name} rejected!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/admin/deactivate', methods=['POST'])
def deactivate_topic():
    """Deactivate an active topic"""
    data = request.json
    topic_name = data.get('topic_name')
    
    try:
        update_topic_status(topic_name, 'deactivated')
        return jsonify({'success': True, 'message': f'Topic {topic_name} deactivated!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Producer API Routes

@app.route('/api/producer/topics/<int:producer_id>')
def get_producer_topics(producer_id):
    """Get topics created by a specific producer (returns all topics for now)"""
    all_topics = get_all_topics()
    return jsonify([{
        'topic_name': t['name'],
        'status': t['status'],
        'created_at': str(t['created_at'])
    } for t in all_topics])

@app.route('/api/producer/create', methods=['POST'])
def create_topic_api():
    """Create a new topic request"""
    data = request.json
    producer_id = data.get('producer_id')
    topic_name = data.get('topic_name')
    
    try:
        success = add_topic(topic_name, 'pending')
        if success:
            return jsonify({'success': True, 'message': f'Topic request "{topic_name}" created! Waiting for admin approval.'})
        else:
            return jsonify({'success': False, 'message': 'Topic already exists or error occurred'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/producer/send', methods=['POST'])
def send_message_api():
    """Send a message to a topic"""
    data = request.json
    producer_id = data.get('producer_id')
    topic_name = data.get('topic_name')
    message = data.get('message')
    
    try:
        # Check if topic is active
        topics = get_topics_by_status('active')
        topic_names = [t[0] for t in topics]
        
        if topic_name not in topic_names:
            return jsonify({'success': False, 'message': 'Topic is not active or does not exist'})
        
        # Send message to Kafka
        producer = KafkaProducer(
            bootstrap_servers=config['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        message_data = {
            'producer_id': producer_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        producer.send(topic_name, message_data)
        producer.flush()
        producer.close()
        
        return jsonify({'success': True, 'message': f'Message sent to {topic_name} successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Consumer API Routes

@app.route('/api/consumer/subscriptions/<int:consumer_id>')
def get_consumer_subscriptions(consumer_id):
    """Get subscriptions for a specific consumer"""
    topic_names = get_user_subscriptions(consumer_id)
    # get_user_subscriptions returns list of topic names (strings)
    return jsonify([{
        'topic_name': topic_name
    } for topic_name in topic_names])

@app.route('/api/consumer/subscribe', methods=['POST'])
def subscribe_api():
    """Subscribe to a topic"""
    data = request.json
    consumer_id = data.get('consumer_id')
    topic_name = data.get('topic_name')
    
    try:
        # Check if topic is active
        topics = get_topics_by_status('active')
        topic_names = [t['name'] for t in topics]
        
        if topic_name not in topic_names:
            return jsonify({'success': False, 'message': 'Topic is not active or does not exist'})
        
        success = subscribe_user_to_topic(consumer_id, topic_name)
        if success:
            return jsonify({'success': True, 'message': f'Subscribed to {topic_name} successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Subscription failed or already exists'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/consumer/unsubscribe', methods=['POST'])
def unsubscribe_api():
    """Unsubscribe from a topic"""
    data = request.json
    consumer_id = data.get('consumer_id')
    topic_name = data.get('topic_name')
    
    try:
        success = unsubscribe_user_from_topic(consumer_id, topic_name)
        if success:
            return jsonify({'success': True, 'message': f'Unsubscribed from {topic_name}'})
        else:
            return jsonify({'success': False, 'message': 'Unsubscribe failed or subscription not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Store messages in memory for demo (in production, use proper message queue)
consumer_messages = {}

@app.route('/api/consumer/messages/<int:consumer_id>')
def get_consumer_messages(consumer_id):
    """Get messages for a consumer (demo - returns recent messages from subscribed topics)"""
    try:
        # Get consumer's subscriptions
        subscribed_topics = get_user_subscriptions(consumer_id)  # Returns list of topic names
        
        if not subscribed_topics:
            return jsonify([])
        
        # For demo purposes, return stored messages
        messages = consumer_messages.get(consumer_id, [])
        return jsonify(messages[-20:])  # Return last 20 messages
        
    except Exception as e:
        return jsonify([])

def main():
    """Initialize and run the Flask app"""
    print("🚀 Initializing Kafka Dynamic Stream Interactive UI...")
    
    # Initialize database
    initialize_database()
    print("✓ Database initialized")
    
    print(f"\n{'='*60}")
    print("🌐 Web UI Starting...")
    print(f"{'='*60}")
    print(f"\n📍 Access the dashboard at:")
    print(f"   Local:   http://localhost:8080")
    print(f"   Network: http://192.168.191.183:8080")
    print(f"\n{'='*60}\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=False
    )

if __name__ == '__main__':
    main()
