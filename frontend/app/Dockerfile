FROM node:20-alpine AS builder

ARG APP_HOME=/shoulder-to-shoulder
ARG VITE_API_BASE_URL=http://localhost:8080/api/v1
ARG VITE_OSRM_BASE_URL=https://router.project-osrm.org
ARG VITE_APP_ENV=development
ARG VITE_DEBUG=true

ENV APP_HOME=${APP_HOME} \
    VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_OSRM_BASE_URL=${VITE_OSRM_BASE_URL} \
    VITE_APP_ENV=${VITE_APP_ENV} \
    VITE_DEBUG=${VITE_DEBUG}

WORKDIR ${APP_HOME}/frontend/app

COPY frontend/app/package*.json ./
RUN npm install

COPY frontend/app/index.html ./
COPY frontend/app/public ./public
COPY frontend/app/src ./src
COPY frontend/app/vite.config.js ./vite.config.js
COPY frontend/app/postcss.config.js ./postcss.config.js
COPY frontend/app/tailwind.config.js ./tailwind.config.js

RUN npm run build

FROM node:20-alpine

ARG APP_HOME=/shoulder-to-shoulder

ENV APP_HOME=${APP_HOME} \
    NODE_ENV=production

WORKDIR ${APP_HOME}/frontend/app

COPY --from=builder ${APP_HOME}/frontend/app/package*.json ./
COPY --from=builder ${APP_HOME}/frontend/app/node_modules ./node_modules
COPY --from=builder ${APP_HOME}/frontend/app/dist ./dist

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
    CMD node -e "fetch('http://127.0.0.1:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
