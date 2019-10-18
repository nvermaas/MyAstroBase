FROM nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY astrobase.conf /etc/nginx/conf.d/

# build the image like this:
# docker build -t astrobase_nginx_dev .

# run the container from here, like this:
# docker run -d --name astrobase_nginx_dev -p 8018:8018 --mount type=bind,source="$(pwd)",target=/etc/nginx/conf.d/ --restart always astrobase_nginx_dev
