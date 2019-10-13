FROM nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY atdb.conf /etc/nginx/conf.d/

# build the image like this:
# docker build -t atdb_nginx_dev .

# run the container from here, like this:
# docker run -d --name atdb_nginx_dev -p 8010:8010 --mount type=bind,source="$(pwd)",target=/etc/nginx/conf.d/ --restart always atdb_nginx_dev
