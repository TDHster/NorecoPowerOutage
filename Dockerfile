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
# COPY main.py .
# COPY wix_parser.py .
# COPY run_script.sh .

RUN chmod +x run_script.sh

# Копируем crontab
COPY app-cron /etc/cron.d/app-cron

# Права и владелец — критично
RUN chmod 0644 /etc/cron.d/app-cron
RUN chown root:root /etc/cron.d/app-cron

# Создаём лог-файл
RUN touch /var/log/cron.log

# Запускаем cron и следим за логом
CMD ["bash", "-c", "service cron start && tail -f /var/log/cron.log"]