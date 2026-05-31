FROM node:20-alpine

WORKDIR /app

ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ARG VITE_APP_ENV=production
ARG VITE_DEBUG=false

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_APP_ENV=${VITE_APP_ENV} \
    VITE_DEBUG=${VITE_DEBUG}

COPY frontend/app/package*.json ./
RUN npm ci

COPY frontend/app ./
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
