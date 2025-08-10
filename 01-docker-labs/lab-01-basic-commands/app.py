#!/usr/bin/env python3
"""
Working Flask application for Docker Lab 01
Tests: Container networking, volumes, and basic operations
"""

from flask import Flask, jsonify, send_file, request
import os
import socket
import datetime
import json
from pathlib import Path

app = Flask(__name__)

# Data directory for volume testing
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(exist_ok=True)

# Counter file for persistence testing
COUNTER_FILE = DATA_DIR / "counter.txt"

def get_counter():
    """Get persistent counter value"""
    try:
        if COUNTER_FILE.exists():
            return int(COUNTER_FILE.read_text())
    except:
        pass
    return 0

def increment_counter():
    """Increment and save counter"""
    count = get_counter() + 1
    COUNTER_FILE.write_text(str(count))
    return count

@app.route('/')
def home():
    """Main endpoint"""
    return jsonify({
        'message': 'Docker Lab 01 - Application Running!',
        'hostname': socket.gethostname(),
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'timestamp': datetime.datetime.now().isoformat(),
        'environment': os.environ.get('APP_ENV', 'development'),
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'lab01-app',
        'uptime': datetime.datetime.now().isoformat()
    })

@app.route('/counter')
def counter():
    """Test volume persistence"""
    count = increment_counter()
    return jsonify({
        'count': count,
        'message': f'This page has been visited {count} times',
        'persistent': True,
        'data_dir': str(DATA_DIR)
    })

@app.route('/env')
def environment():
    """Display environment variables"""
    env_vars = {k: v for k, v in os.environ.items() 
                if not k.startswith('_') and 'SECRET' not in k}
    return jsonify({
        'environment_variables': env_vars,
        'python_version': os.sys.version,
        'hostname': socket.gethostname()
    })

@app.route('/write', methods=['POST'])
def write_data():
    """Test write to volume"""
    data = request.get_json() or {'message': 'test'}
    filename = DATA_DIR / f"data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f)
    
    return jsonify({
        'status': 'success',
        'file': str(filename),
        'data': data
    })

@app.route('/read')
def read_data():
    """List files in data directory"""
    files = []
    for f in DATA_DIR.glob('*.json'):
        files.append({
            'name': f.name,
            'size': f.stat().st_size,
            'modified': datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat()
        })
    
    return jsonify({
        'files': files,
        'total': len(files),
        'directory': str(DATA_DIR)
    })

@app.route('/static')
def static_page():
    """Serve static HTML file"""
    if os.path.exists('index.html'):
        return send_file('index.html')
    return jsonify({'error': 'index.html not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
