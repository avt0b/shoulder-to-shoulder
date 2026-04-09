# Development stage
FROM node:20-alpine AS dev

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy application sources
COPY vite.config.js ./
COPY index.html ./
COPY public ./public
COPY src ./src

# Expose Vite dev server port
EXPOSE 3000

# Run Vite in container-friendly mode for docker-compose.dev
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# Build stage
FROM dev AS builder

# Accept build arguments
ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_APP_ENV=development
ARG VITE_DEBUG=true

# Set environment variables for build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_APP_ENV=$VITE_APP_ENV
ENV VITE_DEBUG=$VITE_DEBUG

# Build the application
RUN npm run build

# Production stage - use nginx
FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config for SPA
COPY nginx.conf /etc/nginx/conf.d/

# Copy built app from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
