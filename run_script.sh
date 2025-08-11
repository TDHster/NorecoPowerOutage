#!/bin/bash
# run_script.sh

cd /app || exit 1
echo "🔄 Запуск main.py"
python main.py
echo "✅ Завершено"