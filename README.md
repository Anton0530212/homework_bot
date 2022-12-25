# __Telegram-bot__
## _Описание_

Бот, взаимодействующий с API Яндекс.Практикума, для актуализации информации о статусе домашнего задания и перенаправления данных в Telegram-аккаунт. В проекте настроена обработка возникающих ошибок и исключений, а также логирование. 

## _Технологии_

Python 3.7  
python-telegram-bot 13.7

## _Запуск проекта в dev-режиме_

- Установите и активируйте виртуальное окружение
```
py3.7 -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
- в корневой директории проекта создать файл .env и указать:

  PRACTICUM_TOKEN: токен Яндекс.Практикума ([как получить?](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a))  
TELEGRAM_TOKEN: токен Telegram-бота, полученный от BotFather ([как получить?](https://core.telegram.org/bots/features#botfather))  
TELEGRAM_CHAT_ID: id Telegram-аккаунта для получения собщений ([как получить?](https://t.me/userinfobot))  

- после импортирования в проект в качестве константных значений токенов и id, указанных в файле _.env_, бот готов к запуску

Более подробно с информацией о создании Telegram-ботов можно ознакомиться в [официальной документации](https://core.telegram.org/bots/api).

## _Разработчики_
[Плотицын Антон](https://github.com/Anton0530212)
