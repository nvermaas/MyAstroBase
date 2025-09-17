FROM python:3.10-slim
#FROM python:3.9.7-slim

RUN apt-get update && apt-get install --no-install-recommends -y bash nano mc

ENV PYTHONUNBUFFERED 1

RUN mkdir /src
WORKDIR /src
COPY . /src/
RUN pip install -r requirements/prod.txt
RUN exec python manage.py collectstatic --settings=astrobase.settings.docker --no-input
CMD exec gunicorn astrobase.wsgi_docker:application --bind 0.0.0.0:8000 --workers 3 --timeout 120

# build the image like this:
# docker build -t my_astrobase:latest .

# run the container like this:
# docker run -d --name my_astrobase --mount type=bind,source=$HOME/shared,target=/shared -p 8008:8000 --restart always my_astrobase:latest

# log into the container
# docker exec -it my_astrobase sh
