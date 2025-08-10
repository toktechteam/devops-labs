#!/usr/bin/env python3
"""
Unit tests for the CI/CD demo application
"""

import unittest
import json
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app

class TestApp(unittest.TestCase):
    """Test cases for the Flask application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_endpoint(self):
        """Test the home endpoint returns correct structure"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('application', data)
        self.assertIn('version', data)
        self.assertIn('build', data)
        self.assertEqual(data['application'], 'Jenkins CI/CD Demo')
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('checks', data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_ready_endpoint(self):
        """Test readiness probe endpoint"""
        response = self.app.get('/ready')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('ready', data)
        self.assertTrue(data['ready'])
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = self.app.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/plain')
        
        # Check for Prometheus format
        metrics = response.data.decode('utf-8')
        self.assertIn('# HELP', metrics)
        self.assertIn('# TYPE', metrics)
        self.assertIn('app_info', metrics)
    
    def test_api_status_endpoint(self):
        """Test API status endpoint"""
        response = self.app.get('/api/v1/status')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('api_version', data)
        self.assertIn('status', data)
        self.assertIn('endpoints', data)
        self.assertEqual(data['api_version'], 'v1')
        self.assertEqual(data['status'], 'operational')
    
    def test_echo_endpoint(self):
        """Test echo POST endpoint"""
        test_data = {'message': 'Hello Jenkins', 'test': True}
        response = self.app.post('/api/v1/echo',
                                data=json.dumps(test_data),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('echo', data)
        self.assertIn('received_at', data)
        self.assertEqual(data['echo'], test_data)
    
    def test_404_handler(self):
        """Test 404 error handler"""
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Not Found')
    
    def test_response_headers(self):
        """Test response headers are correct"""
        response = self.app.get('/')
        self.assertEqual(response.content_type, 'application/json')

class TestIntegration(unittest.TestCase):
    """Integration tests for the application"""
    
    def setUp(self):
        """Set up test client with environment variables"""
        os.environ['APP_VERSION'] = '2.0.0-test'
        os.environ['BUILD_NUMBER'] = '42'
        os.environ['ENVIRONMENT'] = 'testing'
        
        self.app = app.test_client()
        self.app.testing = True
    
    def test_environment_variables(self):
        """Test that environment variables are used correctly"""
        response = self.app.get('/')
        data = json.loads(response.data)
        
        self.assertEqual(data['version'], '2.0.0-test')
        self.assertEqual(data['build']['number'], '42')
        self.assertEqual(data['environment'], 'testing')
    
    def tearDown(self):
        """Clean up environment variables"""
        if 'APP_VERSION' in os.environ:
            del os.environ['APP_VERSION']
        if 'BUILD_NUMBER' in os.environ:
            del os.environ['BUILD_NUMBER']
        if 'ENVIRONMENT' in os.environ:
            del os.environ['ENVIRONMENT']

if __name__ == '__main__':
    unittest.main()
