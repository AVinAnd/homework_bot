import requests


class CheckTokenError(Exception):
    """Отсутствует необходимая переменная окружения"""
    def __str__(self):
        return 'Отсутствует переменная окружения'


class EndPointError(Exception):
    """Ошибка доступа к эндпоинту"""
    def __str__(self):
        return 'Эндпоинт не доступен'


class HomeWorkStatusError(Exception):
    """Статус работы не соответствует ожидаемому"""
    def __str__(self):
        return 'Статус домашней работы не определен'


class SendMessageError(Exception):
    """Ошибка при отправке сообщения в tg"""
    def __str__(self):
        return 'Сбой при отправке сообщения'


class APIKeyError(Exception):
    """В ответе от API нет ожидаемых ключей"""
    def __str__(self):
        return 'Ответ API не содержит ожидаемые ключи'


class ResponseJsonError(Exception):
    """Ошибка формата ответа API"""
    def __str__(self):
        return 'Ответ API не в формате JSON'


class EmptyListError(Exception):
    """Список домашних работ пуст"""
    def __str__(self):
        return 'Нет актуальных работ'
