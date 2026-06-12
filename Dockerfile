FROM node:20-alpine AS next-builder
WORKDIR /web
COPY web/package.json web/package-lock.json* ./
RUN npm install --frozen-lockfile
COPY web/ .
RUN npm run build

FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ind \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=next-builder /web/out /app/web-out

ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "30"]
# force fresh build
