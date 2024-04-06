FROM python:3.10-slim
#FROM python:3.9.7-slim

RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc libmagic1 git

# Add GPG keys
RUN apt-get update && \
    apt-get install -y gnupg && \
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 0E98404D386FA1D9 6ED0E7B82643E131 F8D2585B8783D481 && \
    apt-get clean

# Update package lists
RUN apt-get update

ENV PYTHONUNBUFFERED 1

RUN mkdir /src
WORKDIR /src
COPY . /src/
RUN pip install -r requirements/prod.txt
RUN exec python manage.py collectstatic --settings=astrobase.settings.docker --no-input
CMD exec gunicorn astrobase.wsgi_docker:application --bind 0.0.0.0:8000 --workers 3

# build the image like this:
# docker build -t astrobase_web:latest .

# run the container from 'shared', like this:
# docker run -d --name astrobase_rpi --mount type=bind,source=/home/pi/shared,target=/shared -p 8008:8000 --restart always astrobase_web:latest

# log into the container
# docker exec -it astrobase_rpi sh
