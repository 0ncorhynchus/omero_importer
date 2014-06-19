FROM ubuntu:12.04

RUN apt-get update
RUN apt-get install -y openjdk-7-jre zeroc-ice postgresql apache2 libapache2-mod-fcgid nginx wget unzip

RUN mkdir -p /opt/omero
WORKDIR /opt/omero
RUN wget http://downloads.openmicroscopy.org/omero/4.4.8/OMERO.server-4.4.8-ice34-b256.zip
RUN unzip OMERO.server-4.4.8-ice34-b256.zip
RUN ln -s OMERO.server-4.4.8-ice34-b256 OMERO.server

# PostgreSQL
USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER db_user WITH SUPERUSER PASSWORD 'omx';" &&\
    createdb -O db_user omero_database

USER root
RUN useradd omero
RUN mkdir /OMERO
RUN chown -R omero /OMERO

USER omero
WORKDIR /opt/omero/OMERO.server
#RUN bin/omero config set omero.db.name 'omero_database' &&\
#    bin/omero config set omero.db.user 'db_user' &&\
#    bin/omero config set omero.db.pass 'omx'

