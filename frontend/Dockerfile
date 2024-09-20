FROM node:22.9.0-slim AS builder
LABEL author="ig.rudenko"

WORKDIR /app

COPY package*.json /app/

RUN npm ci --omit=dev;

COPY public /app/public
COPY src /app/src
COPY index.html /app
COPY *.json /app
COPY *.ts /app

RUN npm run build


FROM nginx:1.27.1-alpine AS prod

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
