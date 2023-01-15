FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY /etc/ssl/media-editor.crt /etc/ssl/media-editor.crt
COPY /etc/ssl/media-editor.key /etc/ssl/media-editor.key
COPY . /etc/nginx/
