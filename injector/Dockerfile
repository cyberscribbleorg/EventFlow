FROM python:3.8.19-bookworm

# Install cron
RUN apt update  -y && apt install -y cron libpq-dev gcc

# Copy application files
COPY . /app

# Set working directory
WORKDIR /app

# install dependencies
RUN pip install -r /app/requirements.txt

# Start the cron service
# CMD ["/app/start-cron.sh"]
