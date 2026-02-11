FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* /app/
RUN npm install

COPY frontend/ /app/
ENV VITE_API_URL=/api/v1
RUN npm run build

FROM nginx:1.25-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
