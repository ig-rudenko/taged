import os.path
import sys

from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseNotFound
from dateconverter import DateConverter
import elasticsearch
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from taged_web.elasticsearch_control import connect_elasticsearch
from taged_web import elasticsearch_control
from taged_web.models import Tags
from datetime import datetime
import random


def icon_path(file: str):
    icon = 'images/icons/file.png'
    if file.endswith('.doc') or file.endswith('.docx') or file.endswith('.rtf'):
        icon = 'images/icons/docx.png'
    if file.endswith('.xls') or file.endswith('.xlsx') or file.endswith('.xlsm'):
        icon = 'images/icons/xlsx.png'
    if file.endswith('.pdf'):
        icon = 'images/icons/pdf.png'
    if file.endswith('.txt'):
        icon = 'images/icons/txt.png'
    if file.endswith('.drawio'):
        icon = 'images/icons/drawio.png'
    if file.endswith('.xml'):
        icon = 'images/icons/xml.png'
    if file.endswith('.vds') or file.endswith('.vsdx'):
        icon = 'images/icons/visio.png'
    if file.endswith('.rar') or file.endswith('.7z') or file.endswith('.zip') or file.endswith('.tar') or file.endswith('.iso'):
        icon = 'images/icons/archive.png'
    if file.endswith('.png') or file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.jpg') \
            or file.endswith('.bpm'):
        icon = 'images/icons/img.png'
    return icon


@login_required(login_url='accounts/login/')
def autocomplete(request):
    print(request.GET)
    es = elasticsearch_control.connect_elasticsearch()
    titles = elasticsearch_control.get_titles(es, request.GET.get('term'))
    print(titles)
    return JsonResponse({'data': titles})


@login_required(login_url='accounts/login/')
def home(request):

    available_tags = Tags.objects.all() if request.user.is_superuser else Tags.objects.filter(user__username=request.user.username)
    unavailable_tags = list({t.tag_name for t in Tags.objects.all()} - {t.tag_name for t in available_tags})
    print('User:', request.user.username)

    tags_in = tags_off = tags_ = sorted(
        [
            {'tag': t.tag_name, 'checked': False}
            for t in available_tags
        ],
        key=lambda x: x['tag'].lower()  # Сортируем по алфавиту
    )
    data = []
    posts_count = None

    if request.method == 'GET':
        es = connect_elasticsearch()
        data = elasticsearch_control.get_last_published(es)
        posts_count = elasticsearch_control.posts_count()

    if request.method == 'POST':
        print(request.POST)
        es = connect_elasticsearch()
        tags_in = dict(request.POST).get('tags-in')
        tags_off = dict(request.POST).get('tags-off') or []
        tags_off += unavailable_tags

        if not request.POST.get('search', '') and not tags_in:
            return HttpResponseRedirect('/')

        data = elasticsearch_control.find_posts(es, string=request.POST.get('search', ''), tags_in=tags_in, tags_off=tags_off)

        for d in data:
            if isinstance(d['tags'], str):
                d['tags'] = [d['tags']]
            # Проверяем прикрепленные файлы
            if os.path.exists(f'{sys.path[0]}/media/{d["id"]}') and os.listdir(f'{sys.path[0]}/media/{d["id"]}'):
                d['files'] = True
            else:
                d['files'] = False

        tags_in = sorted(
            [
                {'tag': t['tag'], 'checked': True if tags_in and t['tag'] in tags_in else False} for t in tags_
            ],
            key=lambda x: x['tag'].lower()  # Сортируем по алфавиту
        )
        tags_off = sorted(
            [
                {'tag': t['tag'], 'checked': True if tags_off and t['tag'] in tags_off else False} for t in tags_
            ],
            key=lambda x: x['tag'].lower()  # Сортируем по алфавиту
        )

    return render(request, 'home.html',
                  {
                      'posts_count': posts_count,
                      'search_mode': request.method == 'POST',
                      'data': data,
                      'superuser': request.user.is_superuser,
                      'tags_in': tags_in,
                      'tags_off': tags_off,
                      'image': random.randint(0, 9),
                      'search_text': request.POST.get('search') or ''
                  })


@login_required(login_url='accounts/login/')
def edit_post(request, post_id):
    """
    Редактирование существующей записи
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """

    res = {}  # Результат поиска в elasticsearch

    available_tags = [t.tag_name for t in Tags.objects.all()] \
        if request.user.is_superuser else \
        [t.tag_name for t in Tags.objects.filter(user__username=request.user.username)]

    # Прикрепленные файлы
    files = []
    if os.path.exists(f'{sys.path[0]}/media/{post_id}') and os.listdir(f'{sys.path[0]}/media/{post_id}'):
        for f in os.listdir(f'{sys.path[0]}/media/{post_id}'):
            files.append(
                {
                    'name': f,
                    'icon': icon_path(f)
                }
            )
        print(files)

    if request.method == 'GET':
        print(request.GET)
        es = connect_elasticsearch()  # Подключаемся к elasticsearch
        try:
            res = es.get(index='company', id=post_id)['_source']  # Получаем запись по ID
            if isinstance(res['tags'], str):
                res['tags'] = [res['tags']]  # Переводим теги в list
        except elasticsearch.exceptions.NotFoundError:
            print('ID not exist')  # Данный ID не существует
            return render(request, 'errors/404.html', status=404)
        print(res)
        res['superuser'] = request.user.is_superuser
        res['post_id'] = post_id
        res['tags'] = [
                    {'tag': t, 'checked': False if t not in res['tags'] else True}
                    for t in available_tags
                ]  # Определяем, какие теги были добавлены в записе
        res['files'] = files  # Прикрепленные файлы

    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('title') and request.POST.get('input') and request.POST.get('tags_checked'):
            # Если были введены все данные
            es = connect_elasticsearch()  # Подключаемся к elasticsearch

            # Обновляем существующую в elasticsearch запись
            res = elasticsearch_control.update_post(es, 'company', {
                'content': request.POST['input'],
                'published_at': datetime.now(),
                'tags': dict(request.POST)['tags_checked'],
                'title': request.POST['title']
            }, id_=post_id)
            print(res)

            # Прикрепленные файлы
            # Удаляем файлы
            if os.path.exists(f'{sys.path[0]}/media/{post_id}'):
                for f in os.listdir(f'{sys.path[0]}/media/{post_id}'):
                    if not request.POST.get(f'checkbox_{f}'):
                        os.remove(f'{sys.path[0]}/media/{post_id}/{f}')  # Удаляем ненужные файлы
            else:
                os.makedirs(f'{sys.path[0]}/media/{post_id}')
            if request.FILES.get('files'):
                print(request.FILES)
                for file in dict(request.FILES)['files']:  # Для каждого файла
                    print(file)
                    with open(f'{sys.path[0]}/media/{post_id}/{file.name}', 'wb+') as upload_file:
                        for chunk_ in file.chunks():
                            upload_file.write(chunk_)  # Записываем файл
            return HttpResponseRedirect(f'/post/{res["_id"]}')

        else:
            # Если не все поля были указаны
            # Отправляем данные, которые были введены
            res = {
                'title': request.POST.get('title'),
                'content': request.POST.get('input'),
                'tags': [
                        {'tag': t, 'checked': False if t not in dict(request.POST).get('tags_checked') else True}
                        for t in available_tags
                ],
                'error': "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                'files': files
            }

    return render(request, 'edit_post.html', res)


@login_required(login_url='accounts/login/')
def download_file(request, post_id, file_name):
    # Отправляем пользователю файл
    if os.path.exists(f'{sys.path[0]}/media/{post_id}/{file_name}'):
        with open(f'{sys.path[0]}/media/{post_id}/{file_name}', 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
        response['Content-Disposition'] = f'inline; filename={file_name}'
        return response


@login_required(login_url='accounts/login/')
def show_post(request, post_id):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """
    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index='company', id=post_id)['_source']  # Получаем запись по ID
        # Если имеется всего один тег, то он имеет тип str, переводим его в list
        if isinstance(res['tags'], str):
            res['tags'] = [res['tags']]
    except elasticsearch.exceptions.NotFoundError:
        print('ID not exist')
        return render(request, 'errors/404.html', status=404)
    res['superuser'] = request.user.is_superuser
    res['post_id'] = post_id

    d = res['published_at']  # 2021-10-13T14:58:05.866799
    res['published_at'] = str(DateConverter(f'{d[8:10]} {d[5:7]} {d[:4]}')) + ' / ' + d[11:19]

    # Если имеются файлы у записи
    res['files'] = []
    if os.path.exists(f'{sys.path[0]}/media/{post_id}') and os.listdir(f'{sys.path[0]}/media/{post_id}'):
        for file in os.listdir(f'{sys.path[0]}/media/{post_id}'):
            res['files'].append({
                'name': file,
                'icon': icon_path(file)
            })

    return render(request, 'post.html', res)


@login_required(login_url='accounts/login/')
def pre_show_post(request, post_id):
    """
    Выводим содержимое заметки
    :param request: запрос
    :param post_id: ID записи в elasticsearch
    :return:
    """
    es = connect_elasticsearch()  # Подключаемся к elasticsearch
    try:
        res = es.get(index='company', id=post_id)['_source']  # Получаем запись по ID
        print(res)

    except elasticsearch.exceptions.NotFoundError:
        print('ID not exist')
        return JsonResponse({'error': 'not found'})

    return JsonResponse(
        {
            'post': res['content']
        }
    )


@login_required(login_url='accounts/login/')
def create_post(request):
    """
    Создаем новую запись
    :param request: запрос
    :return:
    """

    print(request.POST)
    print(request.FILES)

    available_tags = [t.tag_name for t in Tags.objects.all()] \
        if request.user.is_superuser else \
        [t.tag_name for t in Tags.objects.filter(user__username=request.user.username)]

    if request.method == 'POST':

        # Создаем новую запись
        if request.POST.get('title') and request.POST.get('input') and request.POST.get('tags_checked'):
            es = connect_elasticsearch()
            res = elasticsearch_control.create_post(es, 'company', {
                'content': request.POST['input'],
                'published_at': datetime.now(),
                'tags': dict(request.POST)['tags_checked'],
                'title': request.POST['title']
            })
            print(res)
            if res.get("_id") and request.FILES.get('files'):
                os.makedirs(f'{sys.path[0]}/media/{res["_id"]}')  # Создаем папку для текущей заметки
                print(request.FILES)
                for file in dict(request.FILES)['files']:  # Для каждого файла
                    print(file)
                    with open(f'{sys.path[0]}/media/{res["_id"]}/{file.name}', 'wb+') as upload_file:
                        for chunk_ in file.chunks():
                            upload_file.write(chunk_)  # Записываем файл

            return HttpResponseRedirect(f'/post/{res["_id"]}')

        else:
            tags_checked = dict(request.POST).get('tags_checked') or []     # Выбранные теги
            # Если не все поля были указаны
            return render(request, 'edit_post.html', {
                'title': request.POST.get('title'),
                'content': request.POST.get('input'),
                'tags': [
                    {'tag': t, 'checked': True if t in tags_checked else False}
                    for t in available_tags
                ],
                'error': "Необходимо указать хотя бы один тег, название заметки и её содержимое!",
                'superuser': request.user.is_superuser
            })

    tags_ = sorted(
        [{'tag': t, 'cheched': False} for t in available_tags],
        key=lambda x: x['tag'].lower()  # Сортируем по алфавиту
    )  # Если новая запись, то все теги изначально отключены
    return render(request, 'edit_post.html', {'tags': tags_, 'superuser': request.user.is_superuser})


@login_required(login_url='accounts/login/')
def delete_post(request, post_id):
    # Смотрим разрешенные теги для данного пользователя
    available_tags = [t.tag_name for t in Tags.objects.all()] \
        if request.user.is_superuser else \
        [t.tag_name for t in Tags.objects.filter(user__username=request.user.username)]

    # Подключаемся к Elasticsearch
    es = connect_elasticsearch()

    # Ищем пост по его ID
    post = es.search(index='company', _source=['_id', 'tags'], query={
        "simple_query_string": {
            "query": post_id,
            "fields": ['_id']
        }
    })
    if post['_shards']['successful']:    # Если нашли
        post_tags = post['hits']['hits'][0]['_source']['tags']  # Смотрим его теги

    else:
        print('ID not exist')
        return render(request, 'errors/404.html', status=404)

    # Если теги поста разрешены данному пользователю, то удаляем пост
    print(post_tags)
    print(available_tags)
    if set(post_tags).issubset(available_tags):
        print('delete:', post_id)
        es.delete(index='company', id=post_id)
        if os.path.exists(f'{sys.path[0]}/media/{post_id}'):  # Если есть прикрепленные файлы
            for f in os.listdir(f'{sys.path[0]}/media/{post_id}'):
                os.remove(f'{sys.path[0]}/media/{post_id}/{f}')  # Удаляем файл
            os.rmdir(f'{sys.path[0]}/media/{post_id}')  # Удаляем папку

    return HttpResponseRedirect('/')


@login_required(login_url='accounts/login/')
def tags(request):
    """
    Смотрим и создаем теги
    :param request: запрос
    :return:
    """
    if not request.user.is_superuser:  # Только суперпользователи
        return HttpResponseRedirect('/')

    if request.method == 'GET':
        all_tags = Tags.objects.all()  # Все существующие теги
        return render(request, 'tags.html', {'tags': all_tags})

    if request.method == 'POST':
        # Добавляем новый тег
        if request.POST.get('new_tag'):
            t = Tags()
            t.tag_name = request.POST['new_tag']
            t.save()
        return HttpResponseRedirect('/tags')


@login_required(login_url='accounts/login/')
def delete_tag(request, tag_id):
    """
    Смотрим и создаем теги
    :param request: запрос
    :param tag_id: ID тега
    :return:
    """
    if not request.user.is_superuser:  # Только суперпользователи
        return HttpResponseRedirect('/')

    t = Tags.objects.get(id=tag_id)
    print(t.tag_name)
    t.delete()
    return HttpResponseRedirect('/tags')


@login_required(login_url='accounts/login/')
def users(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    u = User.objects.all()
    return render(request, "user_control/users.html", {"users": u})


@login_required(login_url='accounts/login/')
def user_access_edit(request, username):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    if request.method == 'GET':
        if not username:
            return HttpResponseRedirect('/users')

        data = {}

        for tag in Tags.objects.all():
            try:
                is_enable = Tags.objects.get(id=tag.id).user.get(username=username)
            except Exception:
                is_enable = 0

            data[tag.id] = {
                'name': tag.tag_name,
                'checked': is_enable,
            }

        return render(
            request,
            'user_control/user_access_group.html',
            {
                'username': username,
                'data': data
            }
        )

    elif request.method == 'POST':
        user = User.objects.get(username=username)  # Пользователь
        for tag in Tags.objects.all():
            if request.POST.get(f'tag_id_{tag.id}'):    # Если данная группа была выбрана
                user.tags_set.add(tag)  # Добавляем пользователя в группу
            else:
                user.tags_set.remove(tag)  # Удаляем

        return HttpResponseRedirect('/users')


@login_required(login_url='accounts/login/')
def logout(request):
    return render(request, 'registration/logout.html')
