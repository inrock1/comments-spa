# Build Vue.js app
FROM node:18.16.0 AS build
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install
RUN npm run build
EXPOSE 8080

# Build Django REST Framework
FROM python:3.10-slim
LABEL maintainer="kaskov.e@gmail.com"
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
# RUN apt-get update && apt-get -y install libpq-dev gcc
RUN pip install -r requirements.txt
COPY . .
RUN mkdir -p /attachments/files
RUN mkdir -p /attachments/images

RUN adduser --disabled-password --no-create-home django-user
RUN chown -R django-user:django-user /app/attachments/
RUN chmod -R 755 /attachments/files/
RUN chmod -R 755 /attachments/images/
USER django-user
EXPOSE 8000
