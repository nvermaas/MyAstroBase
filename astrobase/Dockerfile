FROM python:3.6.7-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add bash && apk add nano
RUN mkdir /code
WORKDIR /code
FROM python:3.6.7-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add bash && apk add nano && apk add mc
RUN mkdir /src
WORKDIR /src
COPY . /src/
RUN pip install -r requirements/prod.txt
# RUN exec python manage.py collectstatic --settings=astrobase.settings.docker_rpi
CMD exec gunicorn astrobase.wsgi_docker_rpi:application --bind 0.0.0.0:8008 --workers 3

# build the image like this:
# docker build -t astrobase_web:latest .

# run the container from 'shared', like this:
# sudo docker run -d --name astrobase_rpi --mount type=bind,source="$(pwd)",target=/shared -p 8018:8018 --restart always astrobase_web:latest

# log into the container
# docker exec -it astrobase_rpi sh
