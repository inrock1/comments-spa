# Build Vue.js app
FROM node:18.16.0 AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
RUN npm install -g @vue/cli
RUN npm install vue-axios axios
RUN npm install moment --save
RUN npm install vue-image-upload-resize
RUN npm install vue-recaptcha
COPY frontend/ .
RUN npm run build
EXPOSE 8080

