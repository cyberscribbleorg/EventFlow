FROM python:3.8-slim

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy application files
COPY . /app

# Set working directory
WORKDIR /app

# Ensure start-cron.sh is executable
RUN chmod +x /app/start-cron.sh

# Start the cron service
CMD ["/app/start-cron.sh"]