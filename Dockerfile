FROM python:3.12.6-alpine


ENV PYTHONUNBUFFERED=1

RUN addgroup -g 10001 appgroup \
    && adduser -D -h /app -u 10002 app appgroup \
    && chown -R app:app /app;

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir "media";


COPY --chown=app:app elasticsearch_control /app/elasticsearch_control
COPY --chown=app:app taged /app/taged
COPY --chown=app:app taged_web /app/taged_web
COPY --chown=app:app manage.py /app/manage.py
COPY --chown=app:app mypy.ini /app/mypy.ini
COPY --chown=app:app run.sh /app/run.sh

RUN chmod +x /app/run.sh

EXPOSE 8000

USER app

CMD ["/bin/sh", "/app/run.sh"]
