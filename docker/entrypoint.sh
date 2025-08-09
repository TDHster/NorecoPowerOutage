#!/bin/bash

echo "Container started at $(date)"

# Очищаем старые cron задачи
crontab -r 2>/dev/null || true

# Копируем переменные окружения для cron
printenv | grep -v "^_" > /etc/environment

# Устанавливаем cron задачу
crontab /etc/cron.d/cleanup-cron

echo "Cron jobs installed:"
crontab -l

# Тестируем скрипт сразу
echo "Testing script execution..."
/app/run_script.sh

# Запускаем cron в фоне
cron

# Следим за логами cron и приложения
touch /var/log/cron.log
tail -f /var/log/cron.log &
# Дополнительный процесс для вывода логов приложения
tail -f /proc/1/fd/1