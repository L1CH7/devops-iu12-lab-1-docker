FROM nginx:1.27-alpine

# Копирование файла конфигурации Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копирование статических файлов
COPY html/ /usr/share/nginx/html/

EXPOSE 80
