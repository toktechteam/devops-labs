require 'sinatra'
require 'json'
require 'socket'

class GitLabDemoApp < Sinatra::Base
  set :port, ENV['PORT'] || 4567
  set :bind, '0.0.0.0'
  set :environment, ENV['RACK_ENV'] || 'development'

  # Application info
  APP_VERSION = ENV['APP_VERSION'] || '1.0.0'
  CI_COMMIT_SHA = ENV['CI_COMMIT_SHA'] || 'local'
  CI_PIPELINE_ID = ENV['CI_PIPELINE_ID'] || '0'
  CI_JOB_ID = ENV['CI_JOB_ID'] || '0'

  # Root endpoint
  get '/' do
    content_type :json
    {
      message: 'GitLab CI/CD Demo Application',
      version: APP_VERSION,
      hostname: Socket.gethostname,
      gitlab: {
        commit_sha: CI_COMMIT_SHA[0..7],
        pipeline_id: CI_PIPELINE_ID,
        job_id: CI_JOB_ID
      },
      timestamp: Time.now.iso8601
    }.to_json
  end

  # Health check endpoint
  get '/health' do
    content_type :json
    {
      status: 'healthy',
      service: 'gitlab-demo-app',
      version: APP_VERSION,
      uptime: Time.now - settings.start_time,
      checks: {
        app: 'operational',
        database: check_database,
        cache: check_cache
      }
    }.to_json
  end

  # Ready endpoint
  get '/ready' do
    content_type :json
    {
      ready: true,
      service: 'gitlab-demo-app',
      timestamp: Time.now.iso8601
    }.to_json
  end

  # Metrics endpoint (Prometheus format)
  get '/metrics' do
    content_type :text
    <<~METRICS
      # HELP app_info Application information
      # TYPE app_info gauge
      app_info{version="#{APP_VERSION}",commit="#{CI_COMMIT_SHA[0..7]}"} 1

      # HELP ruby_version Ruby version info
      # TYPE ruby_version gauge
      ruby_version{version="#{RUBY_VERSION}"} 1

      # HELP app_uptime_seconds Application uptime
      # TYPE app_uptime_seconds gauge
      app_uptime_seconds #{Time.now - settings.start_time}

      # HELP http_requests_total Total HTTP requests
      # TYPE http_requests_total counter
      http_requests_total{method="GET",endpoint="/"} #{settings.request_count}
    METRICS
  end

  # API endpoints
  get '/api/info' do
    content_type :json
    {
      api_version: 'v1',
      endpoints: [
        { method: 'GET', path: '/', description: 'Application info' },
        { method: 'GET', path: '/health', description: 'Health check' },
        { method: 'GET', path: '/ready', description: 'Readiness check' },
        { method: 'GET', path: '/metrics', description: 'Prometheus metrics' },
        { method: 'GET', path: '/api/info', description: 'API information' }
      ]
    }.to_json
  end

  # 404 handler
  not_found do
    content_type :json
    status 404
    {
      error: 'Not Found',
      path: request.path_info,
      method: request.request_method
    }.to_json
  end

  # Error handler
  error do
    content_type :json
    status 500
    {
      error: 'Internal Server Error',
      message: env['sinatra.error'].message
    }.to_json
  end

  # Configure settings
  configure do
    set :start_time, Time.now
    set :request_count, 0
  end

  # Before each request
  before do
    settings.request_count += 1
    headers['X-Request-ID'] = SecureRandom.uuid
  end

  private

  def check_database
    # Simulate database check
    'operational'
  end

  def check_cache
    # Simulate cache check
    'operational'
  end
end

# Run the application
GitLabDemoApp.run! if __FILE__ == $0