FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

# Устанавливаем tzdata и часовой пояс
ENV TZ=Asia/Manila
RUN ln -snf /usr/share/zoneinfo/Asia/Manila /etc/localtime \
    && echo "Asia/Manila" > /etc/timezone \
    && DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y cron tzdata \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔥 КЛЮЧЕВАЯ СТРОКА: Указываем, где искать браузеры
ENV PLAYWRIGHT_BROWSERS_PATH=0

# Устанавливаем браузеры — теперь они будут в .local-browsers внутри пакета
RUN python -m playwright install chromium --with-deps

# Копируем скрипты
COPY . .

# Права
RUN chmod +x run_script.sh

# Создаём лог
RUN touch /var/log/cron.log

# Копируем crontab
COPY app-cron /tmp/app-cron

# Запускаем: cron + tail
CMD ["bash", "-c", "crontab /tmp/app-cron && service cron start && tail -f /var/log/cron.log"]