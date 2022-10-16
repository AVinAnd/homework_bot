class CheckTokenError(Exception):
    def __str__(self):
        return 'Отсутствует переменная окружения'


class StatusCodeError(Exception):
    def __str__(self):
        return 'Ошибка запроса. Код != 200'


class EmptyDictError(Exception):
    def __str__(self):
        return 'Домашняя работа не найдена'


class HomeWorkStatusError(Exception):
    def __str__(self):
        return 'Статус домашней работы не определен'
