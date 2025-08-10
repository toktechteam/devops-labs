# Multi-stage Dockerfile for GitHub Actions demo app
FROM node:18-alpine AS deps
WORKDIR /app
COPY src/package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY src/package*.json ./
RUN npm ci
COPY src/ ./
RUN npm run build || echo "No build step"

FROM node:18-alpine AS runner
WORKDIR /app

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy production dependencies
COPY --from=deps --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copy application
COPY --from=builder --chown=nodejs:nodejs /app ./

# Build arguments for metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Labels
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.title="GitHub Actions Demo" \
      org.opencontainers.image.description="Demo application for GitHub Actions CI/CD"

# Environment
ENV NODE_ENV=production \
    PORT=3000 \
    APP_VERSION=${VERSION}

USER nodejs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {r.statusCode === 200 ? process.exit(0) : process.exit(1)})"

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "app.js"]
