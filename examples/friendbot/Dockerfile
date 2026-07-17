FROM python:3.12-slim as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

FROM base as builder
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY examples/friendbot/pyproject.toml examples/friendbot/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project examples/friendbot --no-editable --frozen --no-dev --no-install-workspace

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project examples/friendbot --no-editable --frozen --no-dev

FROM base as runner
COPY --from=builder /app/.venv .venv
ENV PATH="/app/.venv/bin:$PATH"

COPY examples/friendbot/questions.txt ./questions.txt

ENV GROUPS_DB_PATH=/data/groups.db
ENV QUESTION_FILE=/app/questions.txt
ENV LOG_LEVEL=INFO

VOLUME /data

CMD ["friendbot"]
