# Basic Dockerfile - Starting point for Lab 02
# This Dockerfile has intentional issues for learning purposes

FROM python:3.11

# Set working directory
WORKDIR /app

# Copy everything (inefficient)
COPY . .

# Install dependencies (not cached properly)
RUN pip install Flask==2.3.3
RUN pip install Werkzeug==2.3.7

# Expose port
EXPOSE 5000

# Run as root (security issue)
CMD ["python", "app.py"]
