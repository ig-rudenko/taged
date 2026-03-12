FROM python:3.13.12-alpine AS builder

SHELL ["/bin/sh", "-exc"]
ARG python_version=3.13

WORKDIR /app

RUN apk add --no-cache curl \
 && curl -L https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin/:$PATH" \
    UV_PYTHON="python$python_version" \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONOPTIMIZE=1

COPY pyproject.toml uv.lock /app/

RUN --mount=type=cache,destination=/root/.cache/uv uv sync \
  --no-dev \
  --no-install-project \
  --frozen


FROM python:3.13.12-alpine
LABEL authors="ig-rudenko"

ARG user_id=1000
ARG group_id=1001

WORKDIR /app

SHELL ["/bin/sh", "-exc"]

RUN addgroup -g $group_id appgroup \
    && adduser -D -h /app -u $user_id app $group_id \
    && chown -R $user_id:$group_id /app;

ENV PATH=/app/venv/bin:$PATH \
    PYTHONOPTIMIZE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

COPY --chown=$user_id:$group_id . /app
COPY --link --from=builder /app/venv/ /app/venv

RUN chmod +x run.sh

USER $user_id:$group_id
EXPOSE 8000/tcp
STOPSIGNAL SIGINT

CMD ["/bin/sh", "/app/run.sh"]
