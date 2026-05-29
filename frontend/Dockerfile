# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy app files
COPY frontend/app/package*.json ./
RUN npm install

# Copy source
COPY frontend/app/ .

# Build
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_APP_ENV=development
ARG VITE_DEBUG=true

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_APP_ENV=${VITE_APP_ENV}
ENV VITE_DEBUG=${VITE_DEBUG}

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/nginx.conf

# Copy built app from builder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
