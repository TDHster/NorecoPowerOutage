FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем браузеры
RUN python -m playwright install chromium --with-deps


# Копируем скрипты
COPY . .

RUN chmod +x run_script.sh

# Создаём лог
RUN touch /var/log/cron.log

# 🔥 Добавляем задачу в crontab root
RUN echo '16 7 * * * /app/run_script.sh >> /var/log/cron.log 2>&1' | crontab -

# Запускаем cron и tail
# CMD ["bash", "-c", "service cron start && tail -f /var/log/cron.log"]

COPY app-cron /tmp/app-cron
CMD ["bash", "-c", "crontab /tmp/app-cron && service cron start && tail -f /var/log/cron.log"]