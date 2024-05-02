# База знаний

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
[![Code style: black](https://img.shields.io/badge/code_style-black-black.svg)](https://github.com/psf/black)

### Гибкое хранилище записей с разграничением уровня доступа

<div>
<img width="32" height="32" src="https://www.vectorlogo.zone/logos/vuejs/vuejs-icon.svg" alt="VUE.JS"/>
<img width="32" height="32" src="https://cdn.worldvectorlogo.com/logos/django.svg" alt="django"/> 
<img width="32" height="32" src="https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt36f2da8d650732a0/5d0823c3d8ff351753cbc99f/logo-elasticsearch-32-color.svg" alt="elasticsearch"/>
<img width="32" height="32" src="https://www.vectorlogo.zone/logos/sqlite/sqlite-icon.svg" alt="sqlite"/>
</div>


![](static/images/img_3.png)

В качестве WYSIWYG редактора был выбран CKEditor4

![](static/images/img_2.png)

Структура приложения:

![img.png](static/images/img.png)

## Установка

Для работы приложения на сервер необходимо установить:

- python (>3.10)
- docker
- docker-compose

### Настройка SSL

Для работы https требуется сертификат и ключ, их можно создать через скрипт
или поместить уже созданные заранее.

Пути требуемых файлов.

- Ключ RSA - `/etc/ssl/taged/private/nginx-selfsigned.key`

- Сертификат - `/etc/ssl/taged/certs/nginx-selfsigned.crt`

- Ключи Диффи-Хеллмана - `/etc/ssl/taged/certs/dhparam.pem`

Создание через скрипт:

```shell
cd settings/nginx
bash create_cert.sh
```

После этого будут созданы необходимые файлы.

### Ansible

Развертывание приложения осуществляется через **ansible**,
который создает и запускает docker контейнеры через **docker-compose**.

Для этого необходимо изменить файл `ansible/hosts`
и указать свои данные для подключения и переменные.

```ini
[knowledge_host]
knowledge_host ansible_host =  # Дополнительные параметры подключения

[knowledge-host:vars]
python_version = 3.11
root_folder = /opt/taged
DJANGO_SECRET_KEY = django-insecure-o$84xxrt-ip(b7&)wy)ka(@s@7tq()0vs0u(hu*mo7-^uvc_54
django_superuser_username = root
django_superuser_password = password
django_superuser_email = superuser@example.com
```

Далее запускаем ansible.

```shell
ansible-playbook -i ansible/hosts ansible/playbooks/deploy.yaml
```
