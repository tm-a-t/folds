FROM python:3.12-slim as base
WORKDIR /app

FROM base as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY examples/comment_enforcer/pyproject.toml examples/comment_enforcer/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project examples/comment_enforcer --no-editable --frozen --no-dev --no-install-workspace

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project examples/comment_enforcer --no-editable --frozen --no-dev

FROM base as runner
COPY --from=builder /app/.venv .venv
ENV PATH="/app/.venv/bin:$PATH"

VOLUME /app/.folds

CMD ["python", "-m", "comment_enforcer"]
