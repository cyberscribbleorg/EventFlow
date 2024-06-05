FROM python:3.8-slim

# Install cron
RUN apt-get update && apt-get install -y cron libpq-dev gcc

# Copy application files
COPY . /app

# Set working directory
WORKDIR /app

# install dependencies
RUN pip install -r /app/requirements.txt

# Start the cron service
# CMD ["/app/start-cron.sh"]