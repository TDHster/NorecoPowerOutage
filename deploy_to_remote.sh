#!/bin/bash
REMOTE_HOST="tdh@rpi.local"
REMOTE_PATH="/home/tdh/noreco" # Измените этот путь, если на удаленном сервере другая директория для проекта
LOCAL_PATH="./" # Текущая директория

echo "Синхронизация локальных файлов с удаленным сервером $REMOTE_HOST:$REMOTE_PATH"
# Используем -a (архивный режим), -v (подробный вывод), -z (сжатие)
# Исключаем сами скрипты из синхронизации
rsync -avz --exclude-from=.rsync-filter "$LOCAL_PATH" "$REMOTE_HOST":"$REMOTE_PATH"

if [ $? -eq 0 ]; then
    echo "Синхронизация на удаленный сервер успешно завершена."
    echo "Выполнение docker compose up --build -d на удаленном сервере..."
    # ssh "$REMOTE_HOST" "cd \"$REMOTE_PATH\" && docker compose up -d --build --remove-orphans && docker compose logs -f --tail=100"
    ssh "$REMOTE_HOST" "cd \"$REMOTE_PATH\" &&  docker compose down && docker compose up -d  --remove-orphans && docker compose logs -f --tail=100"
    if [ $? -eq 0 ]; then
        echo "Команда docker compose успешно выполнена на удаленном сервере."
    else
        echo "Ошибка при выполнении docker compose на удаленном сервере."
    fi
else
    echo "Ошибка при синхронизации на удаленный сервер."
fi
