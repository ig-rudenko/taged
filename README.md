# База знаний

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)


### Гибкое хранилище записей с разграничением уровня доступа

<p>
<img style="vertical-align: center;" src="https://www.vectorlogo.zone/logos/vuejs/vuejs-icon.svg" alt="VUE.JS" width="40" height="40"/>
Vue.js - Frontend
</p>

<p>
<a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer"> 
<img src="https://cdn.worldvectorlogo.com/logos/django.svg" alt="django" width="40" height="40"/> 
</a>
Django - Backend
</p>

<p>
<a href="https://www.elastic.co/elasticsearch/" target="_blank" rel="noreferrer">
<img src="https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt36f2da8d650732a0/5d0823c3d8ff351753cbc99f/logo-elasticsearch-32-color.svg"
    alt="elasticsearch" width="40" height="40"/>
</a>
Elacticsearch - Хранилище записей и поисковый движок
</p>
<p>
<a href="https://www.sqlite.org/" target="_blank" rel="noreferrer">
<img src="https://www.vectorlogo.zone/logos/sqlite/sqlite-icon.svg" alt="sqlite" width="40" height="40"/>
</a>
SQLite - Легкая БД для хранения пользователей
</p>


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


![](static/images/img_3.png)


В качестве WYSIWYG редактора был выбран CKEditor4

![](static/images/img_2.png)

