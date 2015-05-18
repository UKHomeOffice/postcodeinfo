FROM phusion/baseimage:0.9.11

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \
  apt-get update && \
  apt-get -y --force-yes install python-pip python-dev build-essential \
    software-properties-common python-software-properties libpq-dev \
    binutils libproj-dev gdal-bin libgdal-dev python-gdal ncurses-dev

# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full && \
    chown -R www-data:www-data /var/lib/nginx

ADD ./docker/nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default

RUN useradd -m -d /srv/postcodeinfo postcodeinfo

RUN mkdir -p /var/log/wsgi && touch /var/log/wsgi/app.log /var/log/wsgi/debug.log && \
    chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

RUN  mkdir -p /var/log/nginx/postcodeinfo
ADD ./docker/postcodeinfo.ini /etc/wsgi/conf.d/postcodeinfo.ini

# Define mountable directories.
VOLUME ["/var/log/nginx", "/var/log/wsgi"]

# APP_HOME
ENV APP_HOME /srv/postcodeinfo

# Add project directory to docker
ADD . /srv/postcodeinfo
RUN rm -rf /srv/postcodeinfo/.git
RUN chown -R postcodeinfo: /srv/postcodeinfo
RUN cd /srv/postcodeinfo && pip install -r requirements.txt

#ENV DJANGO_DEBUG true
#ENV DJANGO_ALLOWED_HOSTS 127.0.0.1
#ENV SECRET_KEY lkasjdklajskldaksljdklajskldjiu213oi
ENV DJANGO_DB_NAME postcodeinfo
ENV DJANGO_DB_USER postcodeinfo
ENV DJANGO_DB_PASSWORD postcodeinfo
ENV DJANGO_DB_HOST 172.42.1.0
#ENV DJANGO_DB_PORT


EXPOSE 8000
#USER postcodeinfo
WORKDIR /srv/postcodeinfo
