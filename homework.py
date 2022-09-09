import os
import sys
import logging
import time
from http import HTTPStatus

import requests
from telegram import Bot, TelegramError
from requests import RequestException
from dotenv import load_dotenv
from json import JSONDecodeError

from exceptions import IncorrectHttpStatus, ErrorTelegram, \
    NotResponse, JSONError, HomeworksNotList, InvalidStatus

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s'
)
handler = logging.StreamHandler(stream=sys.stdout)


def send_message(bot, message):
    """Просто отправляем сообщение в чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f'{message}')
    except TelegramError:
        raise ErrorTelegram('Ошибка при отправки сообщения')


def get_api_answer(current_timestamp):
    """Делаем запрос к эндпоинту API.

    В случае успешного ответа - возвращаем ответ.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except RequestException:
        raise NotResponse('API не отвечает.')
    if response.status_code != HTTPStatus.OK:
        raise IncorrectHttpStatus(
            'Статус ответа от API не 200.',
            response.status_code,
            response.headers,
            response.url
        )
    try:
        response = response.json()
    except JSONDecodeError:
        raise JSONError(
            'Не удалось преобразовать ответ сервера к типам данных Python!'
        )
    return response


def check_response(response):
    """Проверяем ответ API.

    В случае корректности - возвращаем 'homeworks'.
    """
    if not isinstance(response, dict):
        raise TypeError(
            'Ответ от API ошибочного типа, не словарь!'
        )
    if 'homeworks' not in response:
        raise KeyError(
            'В ответе от API нет ключа "homeworks" с работами!'
        )
    if not isinstance(response['homeworks'], list):
        raise HomeworksNotList(
            'Ответ от API с домашними работами ошибочного типа, не список!'
        )
    return response['homeworks']


def parse_status(homework):
    """Извлекаем из 'homeworks' статус.

    В случае успеха, возвращаем вердикт.
    """
    if 'homework_name' not in homework:
        raise KeyError('У домашней работы нет имени!')
    if 'status' not in homework:
        raise KeyError('У домашней работы нет статуса!')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise InvalidStatus(f'Статус {homework_name} ДЗ не действительный.')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем, что все токены на месте."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    statuses = []
    if check_tokens() is False:
        logging.critical('Не хватает токенов, выход из системы.')
        sys.exit()
    last_error = ''
    while True:
        try:
            response = get_api_answer(
                current_timestamp=current_timestamp
            )
            homework = check_response(response)
            status = homework['status']
            statuses.append(status)
            if statuses[-1] != statuses[-2]:
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logging.debug('Статус не изменился')
            if homework[0]['status'] == 'approved':
                current_timestamp = int(time.time())
        except Exception as error:
            logging.error(str(error))
            if last_error != str(error):
                message = f'Сбой в работе программы: {str(error)}'
                send_message(bot, message)
                logging.info('Сообщение об ошибке отправлено')
                last_error = str(error)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
