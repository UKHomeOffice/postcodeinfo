FROM phusion/baseimage:0.9.16

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' add-apt-repository ppa:nginx/stable && apt-get update && \
  apt-get -y --force-yes install wget python-dev build-essential ncurses-dev \
  software-properties-common python-software-properties libpq-dev binutils gdal-bin \
  libproj-dev libgdal-dev python-gdal ncurses-dev  postgresql-9.3-postgis-scripts nginx-full

# Due to an ubuntu bug (#1306991) we can't use the ubuntu provided pip package, so we're using
# the recommended way: http://pip.readthedocs.org/en/latest/installing.html#install-pip
RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python2.7

# APP_HOME, if you change this variable make sure you update the files in docker/ too
ENV APP_HOME /srv/postcodeinfo

RUN useradd -m -d ${APP_HOME} postcodeinfo

RUN mkdir -p /var/log/wsgi /var/log/nginx/postcodeinfo
RUN touch /var/log/wsgi/app.log /var/log/wsgi/debug.log
RUN chown -R www-data:www-data /var/log/wsgi && chmod -R g+s /var/log/wsgi

# copy the wsgi and nginx config
ADD ./docker/nginx.conf /etc/nginx/nginx.conf
ADD ./docker/postcodeinfo.ini /etc/wsgi/conf.d/postcodeinfo.ini

# install service files for runit
ADD ./docker/nginx.service /etc/service/nginx/run
ADD ./docker/uwsgi.service /etc/service/uwsgi/run

# Define mountable directories.
VOLUME ["/var/log/nginx", "/var/log/wsgi"]

# Add project directory to docker
WORKDIR ${APP_HOME}
ADD . ${APP_HOME}
RUN rm -rf ${APP_HOME}/.git
RUN chown -R postcodeinfo: ${APP_HOME}
RUN cd ${APP_HOME} && pip install -r requirements.txt

# Configuration for the app. Variables that are commented out will be defaulted
# to whatever is in the settings.py
#ENV DJANGO_DEBUG true
#ENV DJANGO_ALLOWED_HOSTS 127.0.0.1
#ENV SECRET_KEY tfZmYFM7KWWbSujx2F4WZyYAIcUrQRZp
ENV DB_NAME postcodeinfo
ENV DB_USERNAME postcodeinfo
ENV DB_PASSWORD postcodeinfo
ENV DB_HOST postgres
ENV DB_PORT 5432

EXPOSE 80
#USER postcodeinfo

# Use baseimage-docker's init process.
CMD ["/sbin/my_init"]
