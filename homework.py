import os
import logging
import sys
import time

import requests
import telegram
from dotenv import load_dotenv
from http import HTTPStatus

import exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения пользователю."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Отправлено сообщение "{message}"')
    except Exception as error:
        logging.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Отправка запроса и получение ответа от API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == HTTPStatus.OK:
        return response.json()
    else:
        logging.error(f'Эндпоинт {ENDPOINT} не доступен')
        raise exceptions.StatusCodeError


def check_response(response):
    """Проверка ответа API."""
    if isinstance(response, dict):
        homework = response.get('homeworks')
        if len(homework) != 0:
            homework = homework[0]
            return homework
        logging.debug('Список домашних работ пуст')
        raise exceptions.EmptyDictError
    else:
        logging.error('Тип данных ответа API не соответствует ожидаемому')
        raise TypeError


def parse_status(homework):
    """Проверка статуса домашней работы."""
    keys = ('homework_name', 'status')
    for key in keys:
        if key not in homework:
            logging.error(f'отсутствие ключа {key} в ответе API')
            raise KeyError

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        logging.error(f'статус работы "{homework_status}" не определен')
        raise exceptions.HomeWorkStatusError
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка обязательных переменных окружения."""
    tokens = {
        PRACTICUM_TOKEN: 'PRACTICUM_TOKEN',
        TELEGRAM_TOKEN: 'TELEGRAM_TOKEN',
        TELEGRAM_CHAT_ID: 'TELEGRAM_CHAT_ID'
    }

    if bool(PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID) is True:
        return True
    else:
        for token in tokens:
            if bool(token) is not True:
                logging.critical(
                    f'Отсутствует переменная окружения: {tokens[token]}'
                )


def main():
    """Основная логика работы бота."""
    check = check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    old_status = ''
    last_message = ''

    while check is True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if message != old_status:
                send_message(bot, message)
                old_status = message

            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != last_message:
                send_message(bot, message)
                last_message = message

            time.sleep(RETRY_TIME)
        else:
            logging.debug('статус ответа не изменился')
    send_message(bot, 'Ошибка программы: Отсутствует переменная окружения')
    raise exceptions.CheckTokenError


if __name__ == '__main__':
    main()
