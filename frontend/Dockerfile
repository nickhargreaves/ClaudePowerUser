FROM node:22-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

# Where nginx should proxy /api/* to — server-to-server, never seen by the
# browser. Fly: http://taskflow-nh-api.internal:8080 (private 6PN network).
# docker-compose: http://backend:8080 (compose service DNS).
ARG API_UPSTREAM=http://backend:8080

RUN apk add --no-cache gettext

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/nginx.conf.template
RUN envsubst '$API_UPSTREAM' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/default.conf

EXPOSE 8080
