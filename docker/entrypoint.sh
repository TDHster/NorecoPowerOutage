#!/bin/bash
#docker/entrypoint.sh

echo "$(date): Cron job started" >> /var/log/cron.log
cd /app
echo "$(date): Current directory: $(pwd)" >> /var/log/cron.log

if [ -f /app/.env ]; then
  echo "$(date): .env file found" >> /var/log/cron.log
  # Загружаем переменные из .env
  export $(grep -v '^#' /app/.env | grep -v '^$' | xargs)
  echo "$(date): Environment variables loaded" >> /var/log/cron.log
else
  echo "$(date): .env file not found!" >> /var/log/cron.log
fi

echo "$(date): Starting Python script" >> /var/log/cron.log
# Запускаем Python-скрипт с перенаправлением в лог
python /app/main.py >> /var/log/cron.log 2>&1
exit_code=$?
echo "$(date): Python script finished with exit code: $exit_code" >> /var/log/cron.log