FROM node:20-alpine AS builder

ARG APP_HOME=/shoulder-to-shoulder
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_APP_ENV=development
ARG VITE_DEBUG=true

ENV APP_HOME=${APP_HOME} \
    VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_APP_ENV=${VITE_APP_ENV} \
    VITE_DEBUG=${VITE_DEBUG}

WORKDIR ${APP_HOME}/frontend/authorization

COPY frontend/authorization/package*.json ./
RUN npm ci

COPY frontend/authorization/index.html ./
COPY frontend/authorization/public ./public
COPY frontend/authorization/src ./src
COPY frontend/authorization/vite.config.js ./vite.config.js

RUN npm run build

FROM node:20-alpine

ARG APP_HOME=/shoulder-to-shoulder

ENV APP_HOME=${APP_HOME}

WORKDIR ${APP_HOME}/frontend/authorization

RUN apk add --no-cache curl && npm install -g serve

COPY --from=builder ${APP_HOME}/frontend/authorization/dist ./dist

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
    CMD curl -fsS http://localhost:3000/ || exit 1

CMD ["serve", "-s", "dist", "-l", "3000"]
