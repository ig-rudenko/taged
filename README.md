# Taged

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)


### Сервис заметок с тегами + библиотека книг

<div>
В качестве хранилища и поисковика используется

<a href="https://www.elastic.co/elasticsearch/" target="_blank" rel="noreferrer">
<span>Elacticsearch</span>
<img style="vertical-align: middle" src="https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt36f2da8d650732a0/5d0823c3d8ff351753cbc99f/logo-elasticsearch-32-color.svg"
    alt="elasticsearch" width="40" height="40"/>
</a>&nbsp
</div>


## Настройка SSL

Переходим в папку `seettings/nginx`, запускаем скрипт для создания 
сертификата:

```shell
cd settings/nginx
bash create_cert.sh
```

После этого будут созданы три файла:

Ключ RSA на 2048 бит - `settings/nginx/private/nginx-selfsigned.key`

Сертификат - `settings/nginx/certs/nginx-selfsigned.crt`

Ключи Диффи-Хеллмана - `settings/nginx/certs/dhparam.pem`


## Запуск

Запускаем контейнеры:

    docker-compose up -d

Логин: root

Пароль: password

## Поиск по тегам

Указываем, какие теги включить в поиск, а какие необходимо пропускать

Затем пишем интересующую нас строку. Поиск будет и по названию заметки,
и по её содержимому

![](static/images/img_3.png)


### Просмотр заметки
![](static/images/img_2.png)


## Библиотека

Добавление книг и просмотр в браузере

![](static/images/img_1.png)

### Описание книги
![](static/images/img_5.png)