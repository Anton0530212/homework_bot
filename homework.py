import os
import sys
import logging
import time
import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus
from exceptions import IncorrectHttpStatus

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
HOMEWORK_STATUSES = {
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
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f'{message}')


def get_api_answer(current_timestamp):
    """Делаем запрос к эндпоинту API.
    В случае успешного ответа - возвращаем ответ."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != HTTPStatus.OK:
        logging.error('Ошибка запроса')
        raise IncorrectHttpStatus(
            'Статус ответа от API не 200.',
            response.status_code,
            response.headers,
            response.url
        )
    return response.json()


def check_response(response):
    """Проверяем ответ API.
    В случае корректности - возвращаем 'homeworks'."""
    if isinstance(response['homeworks'], list):
        return response['homeworks']
    else:
        raise Exception


def parse_status(homework):
    """Извлекаем из 'homeworks' статус и,
    в случае успеха, возвращаем вердикт."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except TypeError as error:
        logging.error(f'Возникла ошибка {error} при запросе.')


def check_tokens():
    """Проверяем, что все токены на месте."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    statuses = []
    if check_tokens() is False:
        sys.exit()
    else:
        while True:
            try:
                response = get_api_answer(
                    current_timestamp=current_timestamp
                )
                homework = check_response(response)
                status = homework['status']
                statuses.append(status)
                if statuses[0] != statuses[-1]:
                    message = parse_status(homework[0])
                    send_message(bot, message)
                else:
                    logging.debug('Статус не изменился')
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
