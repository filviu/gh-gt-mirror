#!/bin/bash
echo "Starting..."
python /github-mirror.py
echo "Cron will run according to schedule: $CRON_SCHEDULE"
# copy machine environment variables to cron environment
printenv | cat - /etc/crontab > temp && mv temp /etc/crontab
echo "$CRON_SCHEDULE root python /github-mirror.py > /proc/1/fd/1" >> /etc/crontab

## validate cron file
crontab /etc/crontab

cron -L 7 -f
