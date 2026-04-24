FROM node:22-bookworm-slim AS frontend-builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.js eslint.config.js ./
COPY public ./public
COPY src ./src
RUN npm run build


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV LUNA_STATIC_DIR=/app/dist

WORKDIR /app

COPY InnerVoice_Jelly/requirements.txt ./InnerVoice_Jelly/requirements.txt
RUN pip install --no-cache-dir -r InnerVoice_Jelly/requirements.txt

COPY InnerVoice_Jelly ./InnerVoice_Jelly
COPY --from=frontend-builder /app/dist ./dist

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:${PORT:-8000} InnerVoice_Jelly.backend:app"]
