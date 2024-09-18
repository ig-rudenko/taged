FROM python:3.12.6-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir "media";


COPY elasticsearch_control /app/elasticsearch_control
COPY taged /app/taged
COPY taged_web /app/taged_web
COPY manage.py /app/manage.py
COPY mypy.ini /app/mypy.ini
COPY run.sh /app/run.sh

RUN chmod +x /app/run.sh

EXPOSE 8000

CMD ["/bin/sh", "/app/run.sh"]
