FROM ubuntu:12.04

# referred to http://downloads.openmicroscopy.org/omero/4.4.8/OMERO-4.4.8.pdf
# referred to https://docs.docker.com/examples/postgresql_service/
MAINTAINER Suguru Kato kato.suguru.74x@st.kyoto-u.ac.jp

# Install required packages
RUN echo "deb http://ftp.uk.debian.org/debian/ squeeze contrib" >> /etc/apt/sources.list
RUN echo "deb-src http://ftp.uk.debian.org/debian/ squeeze contrib" >> /etc/apt/sources.list
RUN echo "deb http://ftp.uk.debian.org/debian/ squeeze non-free" >> /etc/apt/sources.list
RUN echo "deb-src http://ftp.uk.debian.org/debian/ squeeze non-free" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y openjdk-7-jdk
RUN apt-get install -y unzip build-essential mencoder
RUN apt-get install -y python python-imaging python-numpy python-tables python-matplotlib
RUN apt-get install -y zeroc-ice
RUN apt-get install -y postgresql
RUN apt-get install -y apache2 libapache2-mod-fcgid
RUN apt-get install -y wget

# Install OMERO.server
RUN mkdir -p /opt/omero
WORKDIR /opt/omero
RUN wget http://downloads.openmicroscopy.org/omero/4.4.8/OMERO.server-4.4.8-ice34-b256.zip
RUN unzip OMERO.server-4.4.8-ice34-b256.zip
RUN ln -s OMERO.server-4.4.8-ice34-b256 OMERO.server

# RUN apt-get update
# RUN apt-get install -y openjdk-7-jre zeroc-ice postgresql apache2 libapache2-mod-fcgid nginx wget unzip
#
# RUN mkdir -p /opt/omero
# WORKDIR /opt/omero
# RUN wget http://downloads.openmicroscopy.org/omero/4.4.8/OMERO.server-4.4.8-ice34-b256.zip
# RUN unzip OMERO.server-4.4.8-ice34-b256.zip
# RUN ln -s OMERO.server-4.4.8-ice34-b256 OMERO.server
#
# # PostgreSQL
# USER postgres
#
# RUN /etc/init.d/postgresql start &&\
#     psql --command "CREATE USER db_user WITH SUPERUSER PASSWORD 'omx';" &&\
#     createdb -O db_user omero_database
#
# USER root
# RUN useradd omero
# RUN mkdir /OMERO
# RUN chown -R omero /OMERO
#
# USER omero
# WORKDIR /opt/omero/OMERO.server
# RUN mkdir /tmp/omero
# ENV OMERO_TEMPDIR /tmp/omero
# RUN bin/omero config set omero.db.name 'omero_database' &&\
#     bin/omero config set omero.db.user 'db_user' &&\
#     bin/omero config set omero.db.pass 'omx'
#
