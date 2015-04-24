FROM phusion/baseimage:0.9.11

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \
  apt-get update && \
  apt-get -y --force-yes install python-pip python-dev build-essential \
    software-properties-common python-software-properties libpq-dev \
    binutils libproj-dev gdal-bin

# Install Nginx.
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update
RUN DEBIAN_FRONTEND='noninteractive' apt-get -y --force-yes install nginx-full && \
    chown -R www-data:www-data /var/lib/nginx

ADD ./docker/nginx.conf /etc/nginx/nginx.conf
RUN rm -f /etc/nginx/sites-enabled/default

RUN mkdir -p /var/log/wsgi && touch /var/log/wsgi/app.log /var/log/wsgi/debug.log && \
    chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

RUN  mkdir -p /var/log/nginx/postcodeinfo
ADD ./docker/postcodeinfo.ini /etc/wsgi/conf.d/postcodeinfo.ini

# Define mountable directories.
VOLUME ["/var/log/nginx", "/var/log/wsgi"]

# APP_HOME
ENV APP_HOME /home/app/django

# Add project directory to docker
ADD . /home/app/django
