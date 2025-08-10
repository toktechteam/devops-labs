package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "os/signal"
    "runtime"
    "syscall"
    "time"
)

type Response struct {
    Message   string    `json:"message"`
    Hostname  string    `json:"hostname"`
    Version   string    `json:"version"`
    GoVersion string    `json:"go_version"`
    Timestamp time.Time `json:"timestamp"`
}

type HealthResponse struct {
    Status    string    `json:"status"`
    Uptime    string    `json:"uptime"`
    Timestamp time.Time `json:"timestamp"`
}

var startTime time.Time

func init() {
    startTime = time.Now()
}

func main() {
    // Setup signal handling
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

    // Setup HTTP handlers
    http.HandleFunc("/", rootHandler)
    http.HandleFunc("/health", healthHandler)
    http.HandleFunc("/metrics", metricsHandler)

    // Get port from environment
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    // Start server in goroutine
    server := &http.Server{
        Addr:         ":" + port,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
    }

    go func() {
        log.Printf("Server starting on port %s\n", port)
        if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatalf("Server failed to start: %v\n", err)
        }
    }()

    // Wait for shutdown signal
    <-sigChan
    log.Println("Shutdown signal received, gracefully stopping...")

    if err := server.Close(); err != nil {
        log.Printf("Server close error: %v\n", err)
    }

    log.Println("Server stopped")
}

func rootHandler(w http.ResponseWriter, r *http.Request) {
    hostname, _ := os.Hostname()
    response := Response{
        Message:   "Hello from Go Multi-Stage Docker!",
        Hostname:  hostname,
        Version:   os.Getenv("APP_VERSION"),
        GoVersion: runtime.Version(),
        Timestamp: time.Now(),
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    uptime := time.Since(startTime)
    response := HealthResponse{
        Status:    "healthy",
        Uptime:    uptime.String(),
        Timestamp: time.Now(),
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}

func metricsHandler(w http.ResponseWriter, r *http.Request) {
    var m runtime.MemStats
    runtime.ReadMemStats(&m)

    metrics := map[string]interface{}{
        "uptime_seconds": time.Since(startTime).Seconds(),
        "goroutines":     runtime.NumGoroutine(),
        "memory": map[string]uint64{
            "alloc":      m.Alloc,
            "total_alloc": m.TotalAlloc,
            "sys":        m.Sys,
            "num_gc":     uint64(m.NumGC),
        },
        "cpu_count": runtime.NumCPU(),
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(metrics)
}