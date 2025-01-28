FROM python:3.12.8-slim AS builder

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc;

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir -r requirements.txt;

FROM python:3.12.8-slim
LABEL authors="Igor"

ENV PYTHONUNBUFFERED=1

RUN addgroup --gid 10001 app \
    && adduser --disabled-password --home /app --uid 10001 --gid 10001 app \
    && chown -R app:app /app;

# Копируем зависимости из builder-этапа
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

COPY --chown=app:app . /app

USER app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]