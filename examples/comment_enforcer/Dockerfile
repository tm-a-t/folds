FROM python:3.13-slim-trixie as builder
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# distroless python is at /usr/bin/python
RUN ln -s /usr/local/bin/python /usr/bin/python

COPY pyproject.toml uv.lock ./
COPY examples/comment_enforcer/pyproject.toml examples/comment_enforcer/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --python /usr/bin/python --project examples/comment_enforcer --no-editable --frozen --no-dev --no-install-workspace

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --python /usr/bin/python --project examples/comment_enforcer --no-editable --frozen --no-dev

FROM gcr.io/distroless/python3-debian13:debug
WORKDIR /app
COPY --from=builder /app/.venv .venv
ENV PATH="/app/.venv/bin:$PATH"

VOLUME /app/.folds

ENTRYPOINT ["python", "-m", "comment_enforcer"]
