FROM python:3.11-slim

WORKDIR /app

# Устанавливаем cron и системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости (для кэширования сначала только файл)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Создаем скрипт-обертку для cron задачи с отладкой
RUN echo '#!/bin/bash' > /app/run_script.sh && \
    echo 'echo "$(date): Cron job started" >> /var/log/cron.log' >> /app/run_script.sh && \
    echo 'cd /app' >> /app/run_script.sh && \
    echo 'echo "$(date): Current directory: $(pwd)" >> /var/log/cron.log' >> /app/run_script.sh && \
    echo 'if [ -f /app/.env ]; then' >> /app/run_script.sh && \
    echo '  echo "$(date): .env file found" >> /var/log/cron.log' >> /app/run_script.sh && \
    echo '  export $(cat /app/.env | grep -v "^#" | grep -v "^$" | xargs)' >> /app/run_script.sh && \
    echo '  echo "$(date): Environment variables loaded" >> /var/log/cron.log' >> /app/run_script.sh && \
    echo 'else' >> /app/run_script.sh && \
    echo '  echo "$(date): .env file not found!" >> /var/log/cron.log' >> /app/run_script.sh && \
    echo 'fi' >> /app/run_script.sh && \
    echo 'echo "$(date): Starting Python script" >> /var/log/cron.log' >> /app/run_script.sh && \
    echo '/usr/local/bin/python /app/main.py >> /var/log/cron.log 2>&1' >> /app/run_script.sh && \
    echo 'echo "$(date): Python script finished with exit code: $?" >> /var/log/cron.log' >> /app/run_script.sh && \
    chmod +x /app/run_script.sh

# Копируем файл с задачей для cron
COPY crontab.txt /etc/cron.d/cleanup-cron

# Даем права на cron файл
RUN chmod 0644 /etc/cron.d/cleanup-cron

# Создаем лог файл и даем права
RUN touch /var/log/cron.log && chmod 666 /var/log/cron.log

# Создаем entrypoint скрипт
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'echo "Container started at $(date)"' >> /entrypoint.sh && \
    echo '# Копируем переменные окружения для cron' >> /entrypoint.sh && \
    echo 'printenv | grep -v "^_" > /etc/environment' >> /entrypoint.sh && \
    echo '# Устанавливаем cron задачу' >> /entrypoint.sh && \
    echo 'crontab /etc/cron.d/cleanup-cron' >> /entrypoint.sh && \
    echo 'echo "Cron jobs installed:"' >> /entrypoint.sh && \
    echo 'crontab -l' >> /entrypoint.sh && \
    echo '# Запускаем cron в фоне' >> /entrypoint.sh && \
    echo 'cron' >> /entrypoint.sh && \
    echo '# Следим за логами' >> /entrypoint.sh && \
    echo 'tail -f /var/log/cron.log' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Запуск через entrypoint
CMD ["/entrypoint.sh"]