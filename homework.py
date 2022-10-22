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
    try:
        response = requests.get(**request_params)
        if response.status_code != HTTPStatus.OK:
            raise exceptions.EndPointError
    except Exception:
        raise exceptions.EndPointError

    try:
        response_json = response.json()
    except Exception:
        raise exceptions.ResponseJsonError
    else:
        logging.info('Ответ API получен')
        return response_json


def check_response(response):
    """Проверка ответа API."""
    logging.info('Проверка ответа API на валидность')
    api_keys = ('homeworks', 'current_date')
    if not isinstance(response, dict):
        raise TypeError('Тип данных не соответствует ожидаемому (dict)')

    for key in api_keys:
        if key not in response:
            raise exceptions.APIKeyError

    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise TypeError('Тип данных не соответствует ожидаемому (list)')

    logging.info('Ответ API валиден')
    return homework


def parse_status(homework):
    """Проверка статуса домашней работы."""
    logging.info('Проверка статуса домашней работы')
    keys = ('homework_name', 'status')
    for key in keys:
        if key not in homework:
            raise KeyError(f'Ожидаемый ключ {key} не найден')

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
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for token_name, token_value in tokens.items():
        if not token_value:
            logging.critical(
                f'Отсутствует переменная окружения: {token_name}')
            return False
    logging.info('Проверка успешна')
    return True


def main():
    """Основная логика работы бота."""
    logging.info('Начало работы')
    if not check_tokens():
        sys.exit('Ошибка программы: Отсутствует переменная окружения')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    old_status = ''
    last_message = ''
    message = ''

    while True:
        try:
            logging.info('Выполнение цикла')
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
            else:
                logging.debug('передан пустой список работ')

            if message != old_status:
                send_message(bot, message)
                old_status = message

            current_timestamp = response.get('current_date')
        except exceptions.SendMessageError as error:
            logging.error(error)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != last_message:
                send_message(bot, message)
                last_message = message
        else:
            logging.info('Цикл выполнен без ошибок')
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
