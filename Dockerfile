FROM phusion/baseimage:0.9.11

# Dependencies
RUN DEBIAN_FRONTEND='noninteractive' \
  apt-get update && \
  apt-get -y --force-yes install python-pip python-dev build-essential \
    software-properties-common python-software-properties libpq-dev \
    binutils libproj-dev gdal-bin

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN useradd -m -d /srv/postcodeinfo postcodeinfo

ADD ./requirements.txt /
RUN pip install -r /requirements.txt

ADD . /srv/postcodeinfo
RUN rm -rf /srv/postcodeinfo/.git
RUN chown -R postcodeinfo: /srv/postcodeinfo

EXPOSE 8000
USER postcodeinfo
WORKDIR /srv/postcodeinfo
