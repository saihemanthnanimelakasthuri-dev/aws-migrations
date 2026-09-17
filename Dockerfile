FROM nginx:alpine

COPY welcome-page.html /usr/share/nginx/html/index.html

EXPOSE 80
