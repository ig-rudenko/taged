FROM node:21-alpine3.19 as builder
LABEL author="ig.rudenko"

WORKDIR /app

# this will allow us to run vite and other tools directly
ENV PATH /usr/src/node_modules/.bin:$PATH

COPY package*.json /app/

RUN npm install;

COPY . .

RUN npm run build


FROM nginx:1.25.5-alpine as prod

COPY --from=builder /app/dist /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]