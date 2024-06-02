#!/bin/sh

# Copy the crontab file to the cron directory
crontab /app/crontab.txt

# Start the cron service
cron -f