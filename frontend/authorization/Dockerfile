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

ENV APP_HOME=${APP_HOME} \
    NODE_ENV=production

WORKDIR ${APP_HOME}/frontend/authorization

COPY --from=builder ${APP_HOME}/frontend/authorization/package*.json ./
COPY --from=builder ${APP_HOME}/frontend/authorization/node_modules ./node_modules
COPY --from=builder ${APP_HOME}/frontend/authorization/dist ./dist

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
    CMD node -e "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
