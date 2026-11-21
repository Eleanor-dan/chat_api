FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
 && pip install . -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8000

CMD [ "uvicorn", "chat_api.main:app", "--host", "0.0.0.0", "--port", "8000" ]

