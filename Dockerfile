############################################################
# Dockerfile to run a GA Statistics
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

# Set the file maintainer (your name - the file's author)
MAINTAINER eyp-developers

# Set env variables used in this Dockerfile
# Directory in container for all project files
ENV STATS_SRVHOME=/srv
# Directory in container for project source files
ENV STATS_SRVPROJ=/srv/statistics
# Set the secret key environment variable
ENV STATS_SECRET_KEY=sa78fzt8792eohfluks.dncppgiöudhÖSDUCZP7PWÖUHYDC
# Set the database password environment variable
ENV STATS_DB_PASSWORD=postgres
# Set the django settings environment variable
ENV DJANGO_SETTINGS_MODULE=eypstats.docker

# Update the default application repository sources list
RUN apt-get update && apt-get install -y \
        python python-dev python-pip postgresql libpq-dev \
        python-imaging python-dev python-setuptools \
        libffi-dev libxml2-dev libxslt1-dev \
        libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev \
        liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk

# Create application subdirectories
WORKDIR $STATS_SRVHOME
RUN mkdir media static logs
VOLUME ["$STATS_SRVHOME/media/", "$STATS_SRVHOME/logs/"]

# Copy application source code to SRCDIR
COPY . $STATS_SRVPROJ

# Install Python dependencies
RUN pip install -r $STATS_SRVPROJ/requirements.txt

# Port to expose
EXPOSE 8000

# Copy entrypoint script into the image
WORKDIR $STATS_SRVPROJ
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
