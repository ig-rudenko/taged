#!/bin/bash
# Отключаем индекс
curl -XPOST 'localhost:9200/company/_close?pretty';
# Отключаем индекс
curl -XPOST 'localhost:9200/books/_close?pretty';
# Регистрация хранилища
curl -XPUT 'http://localhost:9200/_snapshot/backup?pretty' -d '{ "type": "fs", "settings": { "location":"/usr/share/elasticsearch/data", "compress":true } }' -H 'Content-Type: application/json';
# Восстанавливаем данные
curl -XPOST 'http://localhost:9200/_snapshot/backup/snapshot/_restore?pretty' -d '{ "ignore_unavailable": true, "include_global_state": false}' -H 'Content-Type: application/json';
# Включаем индекс
curl -XPOST 'localhost:9200/company/_open?pretty';
# Включаем индекс
curl -XPOST 'localhost:9200/books/_open?pretty';
exit 1