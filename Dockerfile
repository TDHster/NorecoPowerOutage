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

# Копируем файл с задачей для cron
COPY crontab.txt /etc/cron.d/cleanup-cron

# Даем права на cron файл
RUN chmod 0644 /etc/cron.d/cleanup-cron

# Регистрируем cron задачи
RUN crontab /etc/cron.d/cleanup-cron

# Создаем лог файл
RUN touch /var/log/cron.log

# Запуск cron в форграунде
CMD ["cron", "-f"]
