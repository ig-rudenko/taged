#!/bin/bash
# Регистрация хранилища
curl -XPUT 'http://localhost:9200/_snapshot/backup?pretty' -d '{ "type": "fs", "settings": { "location":"/usr/share/elasticsearch/data", "compress":true } }' -H 'Content-Type: application/json';
# Удаляем ранее созданный снапшот
curl -XDELETE 'http://localhost:9200/_snapshot/backup/snapshot?pretty'
# Создаем снапшот
curl -XPUT "http://localhost:9200/_snapshot/backup/snapshot?wait_for_completion=true&pretty=true" -d '{ "ignore_unavailable": true }' -H 'Content-Type: application/json';
exit 1