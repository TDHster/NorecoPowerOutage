FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

# Устанавливаем cron
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Копируем скрипты
COPY docker/run_script.sh /app/run_script.sh
COPY docker/entrypoint.sh /entrypoint.sh
COPY crontab.txt /etc/cron.d/cleanup-cron

# Даем права на скрипты
RUN chmod +x /app/run_script.sh /entrypoint.sh

# Даем права на cron файл
RUN chmod 0644 /etc/cron.d/cleanup-cron

# Создаем лог файл и даем права
RUN touch /var/log/cron.log && chmod 666 /var/log/cron.log

# Запуск через entrypoint
CMD ["/entrypoint.sh"]