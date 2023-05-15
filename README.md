# Бот-ассистент

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы.

## Технологии и запуск проекта

Проект написан на языке python. 
Необходимые для работы проекта зависимости описаны в файле requirements.txt

Для запуска проекта:
- Клонируйте репозиторий
``` 
- git clone https://github.com/AVinAnd/homework_bot.git 
```
- Активируйте виртуальное окружение 

```
python -m venv venv
source venv/scripts/activate
```
- Установите зависимости

``` 
pip install -r requirements.txt
```
- Создайте файл .env, добавьте в него переменные окружения
```
PRACTICUM_TOKEN = 'Токен сервиса Практикум.Домашка'
TELEGRAM_TOKEN = 'Токен Telegram бота'
TELEGRAM_CHAT_ID = 'ID Telegram чата, куда бот отправит сообщение'
```
- Запустите проект
```
python manage.py runserver
```

## Что делает бот
- раз в 10 минут проверяет статус отправленной на ревью домашней работы;

- при обновлении статуса отправляет вам соответствующее уведомление в Telegram
(взята ли работа в ревью, проверена ли она, а если проверена — то принята или возвращена на доработку);

- логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

### Об авторе
Андрей Виноградов - python-developer, выпускник Яндекс Практикума по курсу Python-разработчик
