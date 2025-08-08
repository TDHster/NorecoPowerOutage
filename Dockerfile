FROM python:3.11-slim

WORKDIR /app

# Устанавливаем cron и системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости (для кэширования сначала только файл)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Создаем скрипт-обертку для cron задачи
RUN echo '#!/bin/bash' > /app/run_script.sh && \
    echo 'cd /app' >> /app/run_script.sh && \
    echo 'export $(cat /app/.env | grep -v "^#" | xargs)' >> /app/run_script.sh && \
    echo '/usr/local/bin/python /app/main.py' >> /app/run_script.sh && \
    chmod +x /app/run_script.sh

# Создаем файл с задачей для cron
RUN echo "32 0 * * * /app/run_script.sh >> /proc/1/fd/1 2>&1" > /etc/cron.d/cleanup-cron

# Даем права на cron файл
RUN chmod 0644 /etc/cron.d/cleanup-cron

# Регистрируем cron задачи
RUN crontab /etc/cron.d/cleanup-cron

# Создаем лог файл
RUN touch /var/log/cron.log

# Создаем entrypoint скрипт
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'printenv | grep -v "no_proxy" >> /etc/environment' >> /entrypoint.sh && \
    echo 'cron -f' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Запуск через entrypoint
CMD ["/entrypoint.sh"]