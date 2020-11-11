FROM nginx

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/

# if you need extra tooling installed for troubleshooting then uncomment the following line
# RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc

# build and run from the 'shared' directory, which will be mounted as a volume.
# > cd /home/pi/shared

# build the image like this :
# > docker build -t my_nginx .

# run the container from here, like this:
# > docker run -d --name my_nginx -p 80:80 --mount type=bind,source="/home/pi/shared",target=/shared --mount type=bind,source="/home/pi/shared/static",target=/static --restart always my_nginx
# now this works: http://raspiastro/my_astrobase/

# > docker run -d --name my_nginx_82 -p 82:80 --mount type=bind,source="/home/pi/shared",target=/shared --mount type=bind,source="/home/pi/shared",target=/shared --mount type=bind,source="/home/pi/shared/static",target=/static --restart always my_nginx
# now this works: http://uilennest.net:82/my_astrobase/

