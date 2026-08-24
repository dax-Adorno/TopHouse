FROM node:24.15.0-alpine3.23 AS build

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

ARG VITE_API_URL=""
ARG VITE_CONTACT_EMAIL=contacto@tophouse.com
ARG VITE_WHATSAPP_NUMBER
ENV VITE_API_URL=$VITE_API_URL \
    VITE_CONTACT_EMAIL=$VITE_CONTACT_EMAIL \
    VITE_WHATSAPP_NUMBER=$VITE_WHATSAPP_NUMBER

RUN pnpm run build

FROM nginx:1.28.0-alpine3.21 AS runtime

COPY --from=build /app/dist /usr/share/nginx/html
COPY infra/nginx/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1
