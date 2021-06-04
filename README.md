# NamazTime Telegram bot 
[![Python](https://img.shields.io/badge/python-3-blue)](https://www.python.org/downloads/)
[![pyTelegramBotAPI](https://img.shields.io/badge/aiogram-2.13-blue)](https://docs.aiogram.dev/en/latest/)

Исходный код бота [NamazTime](https://t.me/NamazTimeCheEl_Bot) для мессенджера [Telegram](https://telegram.org/). Бот 
выдает время обязательных ежедневных молитв (намаз) для мусульман. 
 
 Для работы используются бесплатные API сервисов:
 - [TomTom](https://developer.tomtom.com), для получения геопозиции (Python библиотека [GeoPy](https://geopy.readthedocs.io)),
 - [GeoNames](http://www.geonames.org), для получения смещения в часах относительно UTC для местности (Python библиотека [GeoPy](https://geopy.readthedocs.io)),
 - [aladhan.com](https://aladhan.com/prayer-times-api), для получения времени намазов на день для определенной местности.

## Возможности!

- Время намазов для выбранной местности: 
  - на текущий день,
  - на следующий день,
  - на выбранную дату.
- Время ближайшего намаза для выбранной местности
- Поиск местности и установка ее для пользователя.

## Версия 1.6.1
- Для правильного определения ближайшего намаза учитывается смещение часового пояса для местности
- Для поиска локации используется сервис TomTom (вместо Nominatim)

## Версия 1.5.0
- Библиотеки GeoPy переведена на асинхронную работу
- Библиотека requests заменена на aiohttp
- Библиотека sqlite3 заменена на aiosqlite

## Версия 1.1.0
Начало перехода на асинхронность.
- Изменена структура проекта
- pyTelegramBotAPI заменен на aiogram
- Для выбора даты использована библиотека [aiogram_calendar](https://github.com/noXplode/aiogram_calendar)

### Todos 
- Изменение структуры таблиц БД, для фиксации дополнительной информации
- Команды для администратора бота
- Формирование отчетов по работе бота