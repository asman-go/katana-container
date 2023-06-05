# Katana Dockerize

Goal: prepare katana to publish in the YCloud.

[katana](https://github.com/projectdiscovery/katana)

Запускаем python wrapper в контейнере, который забирает с s3 список таргетов и запускает katana. Дожидается выполнения и отправляет результат в s3.

## Why do we need the python wrapper

Так как мы не можем создавать конфиги наподобие docker compose (serverless контейнеры не дружат с дисками, а k8s поднимать дорого), то нужен python-обертка, которая возьмет секреты s3, заберет конфиг, запустит katana, а затем положит результат на s3.

## Environments

```dotenv
KATANA_S3_ENDPOINT=https://storage.yandexcloud.net/
KATANA_BUCKET_NAME=example-bucket
S3_ACCESS_KEY=<YOUR-S3-ACCESS-KEY>
S3_SECRET_KEY=<YOUR-S3-SECRET-TOKEN>
PORT=80
```

## Run

```
http://localhost:PORT/run?campaigh=example.com
```