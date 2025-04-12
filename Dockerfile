# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the application files from the current directory to the container's /app directory
COPY . /app

# Install Supervisor to manage multiple processes (e.g., FastAPI and scheduler)
RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce the image size

# Install Python dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Supervisor configuration file into the container
COPY supervisor.conf /etc/supervisor/supervisord.conf

# Expose port 8000 to allow access to the application
EXPOSE 8000

# Use Supervisor to manage both FastAPI and the scheduler (background services)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]