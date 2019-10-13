FROM python:3.6.7-alpine
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add bash && apk add nano
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 pip install -r requirements/prod.txt && \
 pip install https://support.astron.nl/nexus/content/repositories/snapshots/nl/astron/alta/ALTA_interface_lib/ALTA_interface_lib-1.0.0-dev-20180925_011101.tar.gz --upgrade && \
 apk --purge del .build-deps
CMD exec gunicorn atdb.wsgi_docker_vm:application --bind 0.0.0.0:8010 --workers 3

# RUN exec python manage.py collectstatic --settings=atdb.settings.prod
# EXPOSE 8010

# build the image like this:
# docker build -t atdb_web_dev:latest .

# run the container from here, like this:
# sudo docker run -d --name atdb_web_dev -p 8010:8010 --restart always atdb_web_dev:latest