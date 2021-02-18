# NamazTime Telegram bot 
[![Python](https://img.shields.io/badge/python-3-blue)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-1.1-blue)](https://flask.palletsprojects.com/en/1.1.x/)
[![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-3.6-blue)](https://pypi.org/project/pyTelegramBotAPI/)

Исходный код бота [NamazTime](https://t.me/NamazTimeCheEl_Bot) для мессенджера [Telegram](https://telegram.org/). Бот 
выдает время обязательных ежедневных молитв (намаз) для муссульман. 
 
 Для работы используются бесплатные API сервисов:
 - [Nominatim](https://nominatim.openstreetmap.org), для получения геопозиции(Python библиотека [GeoPy](https://geopy.readthedocs.io)),
 - [aladhan.com](https://aladhan.com/prayer-times-api), для получения времени намазов на день для определенной местности.

## Возможности!

- Бот выводит время намазов для выбранной местности: 
  - на текущий день, 
  - на следующий день,
  - на введенную дату.

- Поиск местности и установки ее для пользователя.

### Todos
- Получение времени ближайшего следующего намаза
- Перевести на inline клавиатуру