# Taged

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)


Сервис заметок с тегами + библиотека

В качестве хранилища и поисковика используется [Elacticsearch](https://www.elastic.co/elastic-stack/)

## Установка

**Для запуска требуется более 2Гб свободной оперативной памяти**

Скачиваем репозиторий и переходим в папку

Запускаем контейнеры

    docker-compose up -d

Порт для подключения по http - 8001

Логин: root

Пароль: password

## Поиск по тегам

Указываем, какие теги включить в поиск, а какие необходимо пропускать

Затем пишем интересующую нас строку. Поиск будет и по названию заметки,
и по её содержимому

![](static/images/img_3.png)

### Поиск по части названия заметки

![img.png](static/images/img_4.png)

### Создание новой заметки

Можно добавлять файлы к заметкам

![](static/images/img.png)

### Просмотр заметки
![](static/images/img_2.png)


## Библиотека

Добавление книг и просмотр в браузере

![](static/images/img_1.png)

### Описание книги
![](static/images/img_5.png)