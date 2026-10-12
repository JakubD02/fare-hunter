FROM python:3.13-slim

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
