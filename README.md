# LuckyJet MiniApp — demo Telegram Web App + Bot

Демо-репозиторий мини-аппа в стиле «Lucky Jet / crash», без реальных денег (виртуальные монеты).  
Включает: Telegram-бот (aiogram) и веб-приложение (aiohttp + статический frontend). Встроенная provably-fair механика.

## Быстрый старт (локально)

1. Клонируй репозиторий и создай `.env` на основе `.env.example`.
2. Установи зависимости и запусти:

```bash
# Запуск веб-сервера
cd web
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
