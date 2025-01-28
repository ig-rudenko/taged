#!/bin/bash
# Отключаем индекс
curl -XPOST 'localhost:9200/notes/_close?pretty';
# Регистрация хранилища
curl -XPUT 'http://localhost:9200/_snapshot/backup?pretty' -d '{ "type": "fs", "settings": { "location":"/usr/share/elasticsearch/data", "compress":true } }' -H 'Conten>
# Восстанавливаем данные
curl -XPOST 'http://localhost:9200/_snapshot/backup/snapshot/_restore?pretty' -d '{ "ignore_unavailable": true, "include_global_state": false}' -H 'Content-Type: applic>
# Включаем индекс
curl -XPOST 'localhost:9201/notes/_open?pretty';
exit 1