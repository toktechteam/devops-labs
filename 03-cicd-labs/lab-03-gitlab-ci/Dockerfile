# Multi-stage Dockerfile for Ruby Sinatra application
FROM ruby:3.2-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    postgresql-dev

WORKDIR /app

# Copy Gemfile
COPY src/Gemfile src/Gemfile.lock* ./

# Install gems
RUN bundle config set --local deployment 'true' && \
    bundle config set --local without 'development test' && \
    bundle install --jobs=4 --retry=3

# Final stage
FROM ruby:3.2-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    postgresql-client \
    tzdata && \
    addgroup -g 1000 -S app && \
    adduser -S -u 1000 -G app app

WORKDIR /app

# Copy gems from builder
COPY --from=builder /app/vendor /app/vendor
COPY --from=builder /app/.bundle /app/.bundle

# Copy application
COPY --chown=app:app src/Gemfile src/Gemfile.lock* ./
COPY --chown=app:app src/app.rb src/config.ru ./

# Set environment
ENV RACK_ENV=production \
    PORT=4567 \
    BUNDLE_PATH=/app/vendor/bundle \
    BUNDLE_WITHOUT=development:test

USER app

EXPOSE 4567

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:4567/health || exit 1

CMD ["bundle", "exec", "puma", "-C", "config/puma.rb"]