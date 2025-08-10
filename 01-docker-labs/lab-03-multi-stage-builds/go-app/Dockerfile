# Multi-stage Dockerfile for Go application
# Stage 1: Build
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /build

# Copy go mod files
COPY go.mod go.sum* ./

# Download dependencies
RUN go mod download 2>/dev/null || echo "No go.mod file"

# Copy source code
COPY main.go .

# Build the binary with optimizations
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -ldflags="-w -s -X main.version=$(date +%Y%m%d)" \
    -a -installsuffix cgo -o app main.go

# Stage 2: Create minimal runtime image
FROM scratch

# Copy timezone data and CA certificates from builder
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy the binary from builder
COPY --from=builder /build/app /app

# Set environment variables
ENV PORT=8080 \
    APP_VERSION=1.0.0

# Expose port
EXPOSE 8080

# Run the binary
ENTRYPOINT ["/app"]

# Image size: ~8MB