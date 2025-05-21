FROM python:3.11-alpine AS builder
WORKDIR /app
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine
WORKDIR /app
RUN apk add --no-cache libpq
COPY --from=builder /install /usr/local
COPY . .
RUN find . -name "*.pyc" -delete \
    && find . -name "__pycache__" -exec rm -rf {} + \
    && rm -rf .git* *.md *.yml discussion_board/tests
EXPOSE 8000
RUN adduser -D appuser
USER appuser
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]