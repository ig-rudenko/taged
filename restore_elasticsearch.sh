#!/bin/bash
# Отключаем индекс
curl -XPOST 'localhost:9200/company/_close?pretty';
# Восстанавливаем данные
curl -XPOST 'http://localhost:9200/_snapshot/backup/snapshot/_restore?pretty' -d '{ "ignore_unavailable": true, "include_global_state": false}' -H 'Content-Type: application/json';
# Включаем индекс
curl -XPOST 'localhost:9200/company/_open?pretty';
exit 1