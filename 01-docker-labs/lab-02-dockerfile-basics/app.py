#!/usr/bin/env python3
"""
Working Flask application for Docker Lab 02
Demonstrates Dockerfile concepts and best practices
"""

from flask import Flask, jsonify, request
import os
import socket
import sys
import platform
from datetime import datetime

app = Flask(__name__)

# Application metadata
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
APP_ENV = os.environ.get('APP_ENV', 'development')
BUILD_DATE = os.environ.get('BUILD_DATE', 'unknown')
VCS_REF = os.environ.get('VCS_REF', 'unknown')

@app.route('/')
def home():
    """Main endpoint with system information"""
    return jsonify({
        'message': 'Docker Lab 02 - Dockerfile Basics',
        'version': APP_VERSION,
        'environment': APP_ENV,
        'hostname': socket.gethostname(),
        'platform': {
            'python': sys.version,
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor()
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/health')
def health():
    """Health check endpoint for Docker HEALTHCHECK"""
    return jsonify({
        'status': 'healthy',
        'service': 'lab02-app',
        'version': APP_VERSION,
        'checks': {
            'app': 'running',
            'port': os.environ.get('PORT', 5000)
        }
    }), 200

@app.route('/build-info')
def build_info():
    """Display build-time information"""
    return jsonify({
        'build': {
            'version': APP_VERSION,
            'date': BUILD_DATE,
            'commit': VCS_REF,
            'base_image': os.environ.get('BASE_IMAGE', 'unknown')
        },
        'runtime': {
            'user': os.environ.get('USER', 'unknown'),
            'home': os.environ.get('HOME', '/'),
            'workdir': os.getcwd(),
            'python_path': sys.executable
        }
    })

@app.route('/env')
def environment():
    """Display environment variables (filtered for security)"""
    safe_env = {}
    for key, value in os.environ.items():
        # Filter out sensitive information
        if not any(sensitive in key.upper() for sensitive in ['SECRET', 'PASSWORD', 'KEY', 'TOKEN']):
            safe_env[key] = value
    
    return jsonify({
        'environment_variables': safe_env,
        'total_vars': len(os.environ),
        'filtered_vars': len(os.environ) - len(safe_env)
    })

@app.route('/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing POST requests"""
    data = request.get_json() or {}
    return jsonify({
        'echo': data,
        'received_at': datetime.utcnow().isoformat() + 'Z',
        'content_type': request.content_type
    })

@app.route('/ready')
def ready():
    """Readiness probe endpoint"""
    # Add actual readiness checks here
    checks = {
        'app_initialized': True,
        'dependencies_loaded': True,
        'port_bound': True
    }
    
    if all(checks.values()):
        return jsonify({
            'ready': True,
            'checks': checks
        }), 200
    else:
        return jsonify({
            'ready': False,
            'checks': checks
        }), 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = APP_ENV == 'development'
    
    print(f"Starting Flask application...")
    print(f"Version: {APP_VERSION}")
    print(f"Environment: {APP_ENV}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
