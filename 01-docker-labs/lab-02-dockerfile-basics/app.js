/**
 * Working Node.js application for Docker Lab 02
 * Demonstrates multi-stage builds and optimization
 */

const express = require('express');
const os = require('os');

const app = express();
app.use(express.json());

// Configuration from environment
const PORT = process.env.PORT || 3000;
const APP_VERSION = process.env.APP_VERSION || '1.0.0';
const NODE_ENV = process.env.NODE_ENV || 'development';
const BUILD_DATE = process.env.BUILD_DATE || 'unknown';

// Main endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'Docker Lab 02 - Node.js Application',
        version: APP_VERSION,
        environment: NODE_ENV,
        hostname: os.hostname(),
        platform: {
            type: os.type(),
            platform: os.platform(),
            arch: os.arch(),
            release: os.release(),
            node_version: process.version
        },
        timestamp: new Date().toISOString()
    });
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'lab02-node',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        version: APP_VERSION
    });
});

// Build information
app.get('/build-info', (req, res) => {
    res.json({
        build: {
            version: APP_VERSION,
            date: BUILD_DATE,
            node_version: process.version,
            environment: NODE_ENV
        },
        runtime: {
            pid: process.pid,
            platform: process.platform,
            cwd: process.cwd(),
            execPath: process.execPath
        }
    });
});

// Environment variables (filtered)
app.get('/env', (req, res) => {
    const safeEnv = {};
    const sensitive = ['SECRET', 'PASSWORD', 'KEY', 'TOKEN'];
    
    Object.keys(process.env).forEach(key => {
        if (!sensitive.some(s => key.toUpperCase().includes(s))) {
            safeEnv[key] = process.env[key];
        }
    });
    
    res.json({
        environment_variables: safeEnv,
        total_vars: Object.keys(process.env).length,
        filtered_vars: Object.keys(process.env).length - Object.keys(safeEnv).length
    });
});

// Echo endpoint
app.post('/echo', (req, res) => {
    res.json({
        echo: req.body,
        headers: req.headers,
        received_at: new Date().toISOString()
    });
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
    const metrics = {
        process: {
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            cpu: process.cpuUsage()
        },
        system: {
            loadavg: os.loadavg(),
            totalmem: os.totalmem(),
            freemem: os.freemem(),
            cpus: os.cpus().length
        }
    };
    res.json(metrics);
});

// Readiness probe
app.get('/ready', (req, res) => {
    // Add actual readiness checks
    const checks = {
        app_initialized: true,
        port_bound: true
    };
    
    if (Object.values(checks).every(check => check)) {
        res.json({ ready: true, checks });
    } else {
        res.status(503).json({ ready: false, checks });
    }
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Internal Server Error',
        message: NODE_ENV === 'development' ? err.message : undefined
    });
});

// Start server
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log('====================================');
    console.log('Node.js Application Started');
    console.log('====================================');
    console.log(`Version: ${APP_VERSION}`);
    console.log(`Environment: ${NODE_ENV}`);
    console.log(`Port: ${PORT}`);
    console.log(`Node Version: ${process.version}`);
    console.log(`PID: ${process.pid}`);
    console.log('====================================');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing HTTP server');
    server.close(() => {
        console.log('HTTP server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT signal received: closing HTTP server');
    server.close(() => {
        console.log('HTTP server closed');
        process.exit(0);
    });
});
