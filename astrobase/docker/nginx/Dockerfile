FROM nginx
RUN apk update && apk add bash && apk add nano && apk add mc
RUN rm /etc/nginx/conf.d/default.conf
COPY astrobase.conf /etc/nginx/conf.d/

# build the image like this:
# docker build -t astrobase_nginx .

# run the container from here, like this:
# docker run -d --name astrobase_nginx -p 8018:8018 --mount type=bind,source="$(pwd)",target=/etc/nginx/conf.d/ --restart always astrobase_nginx
