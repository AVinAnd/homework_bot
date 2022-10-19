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

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения пользователю."""
    logging.info('Отправка сообщения пользователю')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Отправлено сообщение "{message}"')
    except Exception:
        raise exceptions.SendMessageError


def get_api_answer(current_timestamp):
    """Отправка запроса и получение ответа от API."""
    logging.info('Отправка запроса к API')
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    request_params = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': params
    }
    response = requests.get(**request_params)
    if response.status_code != HTTPStatus.OK:
        raise exceptions.EndPointError
    logging.info('Ответ API получен')
    return response.json()


def check_response(response):
    """Проверка ответа API."""
    logging.info('Проверка ответа API на валидность')
    api_keys = ('homeworks', 'current_date')
    if not isinstance(response, dict):
        raise TypeError
    else:
        for key in api_keys:
            if key not in response:
                raise exceptions.APIKeyError

        homework = response.get('homeworks')
        if not isinstance(homework, list):
            raise TypeError

        if len(homework) != 0:
            homework = homework[0]

        logging.info('Ответ API валиден')
        return homework


def parse_status(homework):
    """Проверка статуса домашней работы."""
    logging.info('Проверка статуса домашней работы')
    if len(homework) == 0:
        logging.info('Список работ пуст')
        return 'Нет актуальных работ'

    keys = ('homework_name', 'status')
    for key in keys:
        if key not in homework:
            raise KeyError

    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise exceptions.HomeWorkStatusError
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка обязательных переменных окружения."""
    logging.info('Проверка переменных окружения')
    tokens = {
        PRACTICUM_TOKEN: 'PRACTICUM_TOKEN',
        TELEGRAM_TOKEN: 'TELEGRAM_TOKEN',
        TELEGRAM_CHAT_ID: 'TELEGRAM_CHAT_ID'
    }
    for token in tokens:
        if not token:
            logging.critical(
                f'Отсутствует переменная окружения: {tokens[token]}')
            return False
    logging.info('Проверка успешна')
    return True


def main():
    """Основная логика работы бота."""
    logging.info('Начало работы')
    check = check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    old_status = ''
    last_message = ''

    if not check:
        send_message(bot, 'Ошибка программы: Отсутствует переменная окружения')
        raise exceptions.CheckTokenError

    while check:
        try:
            logging.info('Проверка статуса работы')
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if message != old_status:
                send_message(bot, message)
                old_status = message

            current_timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != last_message:
                send_message(bot, message)
                last_message = message
        else:
            logging.debug('статус ответа не изменился')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        filename='main.log',
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(lineno)d, %(message)s'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s, %(levelname)s, %(lineno)d, %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logger = logging.getLogger(__name__)

    main()
