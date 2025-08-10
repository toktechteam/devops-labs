#!/usr/bin/env python3
"""
CI/CD Demo Application for Jenkins Lab
A simple Flask application with endpoints for testing CI/CD pipelines
"""

from flask import Flask, jsonify, request
import os
import socket
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Application configuration
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
BUILD_NUMBER = os.environ.get('BUILD_NUMBER', 'local')
BUILD_ID = os.environ.get('BUILD_ID', 'unknown')
GIT_COMMIT = os.environ.get('GIT_COMMIT', 'unknown')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

@app.route('/')
def home():
    """Main endpoint returning application information"""
    return jsonify({
        'application': 'Jenkins CI/CD Demo',
        'version': APP_VERSION,
        'build': {
            'number': BUILD_NUMBER,
            'id': BUILD_ID,
            'commit': GIT_COMMIT[:7] if GIT_COMMIT != 'unknown' else 'unknown'
        },
        'environment': ENVIRONMENT,
        'hostname': socket.gethostname(),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    health_status = {
        'status': 'healthy',
        'service': 'jenkins-demo-app',
        'version': APP_VERSION,
        'uptime': get_uptime(),
        'checks': {
            'app': 'running',
            'database': check_database(),
            'dependencies': check_dependencies()
        }
    }
    
    # Return 200 if healthy, 503 if not
    is_healthy = all(health_status['checks'].values())
    return jsonify(health_status), 200 if is_healthy else 503

@app.route('/ready')
def ready():
    """Readiness probe for Kubernetes"""
    ready_status = {
        'ready': True,
        'checks': {
            'initialized': True,
            'database_connected': check_database(),
            'cache_connected': True
        }
    }
    
    is_ready = all(ready_status['checks'].values())
    return jsonify(ready_status), 200 if is_ready else 503

@app.route('/metrics')
def metrics():
    """Prometheus-style metrics endpoint"""
    metrics_data = [
        f'# HELP app_info Application information',
        f'# TYPE app_info gauge',
        f'app_info{{version="{APP_VERSION}",build="{BUILD_NUMBER}"}} 1',
        f'# HELP app_requests_total Total number of requests',
        f'# TYPE app_requests_total counter',
        f'app_requests_total 100',
        f'# HELP app_request_duration_seconds Request duration',
        f'# TYPE app_request_duration_seconds histogram',
        f'app_request_duration_seconds_bucket{{le="0.1"}} 50',
        f'app_request_duration_seconds_bucket{{le="0.5"}} 90',
        f'app_request_duration_seconds_bucket{{le="1.0"}} 99',
        f'app_request_duration_seconds_bucket{{le="+Inf"}} 100'
    ]
    return '\n'.join(metrics_data), 200, {'Content-Type': 'text/plain'}

@app.route('/api/v1/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_version': 'v1',
        'status': 'operational',
        'endpoints': [
            {'path': '/', 'method': 'GET', 'description': 'Application info'},
            {'path': '/health', 'method': 'GET', 'description': 'Health check'},
            {'path': '/ready', 'method': 'GET', 'description': 'Readiness probe'},
            {'path': '/metrics', 'method': 'GET', 'description': 'Prometheus metrics'},
            {'path': '/api/v1/status', 'method': 'GET', 'description': 'API status'},
            {'path': '/api/v1/echo', 'method': 'POST', 'description': 'Echo service'}
        ]
    })

@app.route('/api/v1/echo', methods=['POST'])
def echo():
    """Echo endpoint for testing POST requests"""
    data = request.get_json() or {}
    return jsonify({
        'echo': data,
        'received_at': datetime.utcnow().isoformat() + 'Z',
        'processed_by': socket.gethostname()
    })

@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource does not exist',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Custom 500 handler"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500

def get_uptime():
    """Calculate application uptime"""
    # In a real app, track start time
    return "0d 0h 0m 0s"

def check_database():
    """Simulate database connectivity check"""
    # In a real app, actually check database
    return True

def check_dependencies():
    """Check if all dependencies are available"""
    try:
        import flask
        import gunicorn
        return True
    except ImportError:
        return False

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = ENVIRONMENT == 'development'
    
    logger.info(f"Starting application...")
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Build: {BUILD_NUMBER}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Port: {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
