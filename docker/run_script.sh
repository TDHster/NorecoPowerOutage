#!/bin/bash

echo "$(date): Cron job started"
cd /app
echo "$(date): Current directory: $(pwd)"

if [ -f /app/.env ]; then
  echo "$(date): .env file found"
  # Загружаем переменные из .env
  export $(grep -v '^#' /app/.env | grep -v '^$' | xargs)
  echo "$(date): Environment variables loaded"
else
  echo "$(date): .env file not found!"
fi

echo "$(date): Starting Python script"
# Запускаем Python-скрипт без перенаправления в файл
python /app/main.py
exit_code=$?
echo "$(date): Python script finished with exit code: $exit_code"