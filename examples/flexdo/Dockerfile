FROM python:3.12-slim as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

FROM base as builder
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
COPY examples/flexdo/pyproject.toml examples/flexdo/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project examples/flexdo --no-editable --frozen --no-dev --no-install-workspace

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --project examples/flexdo --no-editable --frozen --no-dev

FROM base as runner
COPY --from=builder /app/.venv .venv
ENV PATH="/app/.venv/bin:$PATH"

VOLUME /app/.folds

CMD ["python", "-m", "flexdo"]
