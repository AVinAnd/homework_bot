class CheckTokenError(Exception):
    """Отсутствует необходимая переменная окружения"""
    def __init__(self, message='Отсутствует переменная окружения'):
        self.message = message
        super().__init__(self.message)


class EndPointError(Exception):
    """Ошибка доступа к эндпоинту"""
    def __init__(self, message='Эндпоинт не доступен'):
        self.message = message
        super().__init__(self.message)


class HomeWorkStatusError(Exception):
    """Статус работы не соответствует ожидаемому"""
    def __init__(self, message='Статус домашней работы не определен'):
        self.message = message
        super().__init__(self.message)


class SendMessageError(Exception):
    """Ошибка при отправке сообщения в tg"""
    def __init__(self, message='Сбой при отправке сообщения'):
        self.message = message
        super().__init__(self.message)


class APIKeyError(Exception):
    """В ответе от API нет ожидаемых ключей"""
    def __init__(self, message='Ответ API не содержит ожидаемые ключи'):
        self.message = message
        super().__init__(self.message)


class ResponseJsonError(Exception):
    """Ошибка формата ответа API"""
    def __init__(self, message='Ответ API не в формате JSON'):
        self.message = message
        super().__init__(self.message)


class EmptyListError(Exception):
    """Список домашних работ пуст"""
    def __init__(self, message='Нет актуальных работ'):
        self.message = message
        super().__init__(self.message)
