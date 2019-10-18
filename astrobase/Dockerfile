FROM python:3.6.7-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add bash && apk add nano
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN pip install -r requirements/prod.txt
CMD exec gunicorn astrobase.wsgi_docker_vm:application --bind 0.0.0.0:8018 --workers 3

# RUN exec python manage.py collectstatic --settings=astrobase.settings.prod
# EXPOSE 8018

# build the image like this:
# docker build -t astrobase_web_dev:latest .

# run the container from 'shared', like this:
# sudo docker run -d --name astrobase_rpi --mount type=bind,source="$(pwd)",target=/shared -p 8018:8018 --restart always astrobase_web_dev:latest &