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
RUN useradd omero
RUN mkdir -p /opt/omero
RUN chown -R omero /opt/omero
USER omero
WORKDIR /opt/omero
RUN wget http://downloads.openmicroscopy.org/omero/4.4.8/OMERO.server-4.4.8-ice34-b256.zip
RUN unzip OMERO.server-4.4.8-ice34-b256.zip
RUN ln -s OMERO.server-4.4.8-ice34-b256 OMERO.server

# Configuration
#RUN echo 'export JAVA_HOME=/usr/lib/jvm/java-6-openjdk' >> /etc/bash.bashrc
#RUN echo 'export ICE_HOME=/usr/share/Ice-1.4.2' >> /etc/bash.bashrc
#RUN echo 'export POSTGRES_HOME=/usr/lib/postgresql/9.1' >> /etc/bash.bashrc
#RUN echo 'export OMERO_PREFIX=/opt/omero/OMERO.server' >> /etc/bash.bashrc
#RUN echo 'export PATH=$PATH:$JAVA_HOME/bin:$ICE_HOME:$POSTGRES_HOME/bin:$OMERO_PREFIX/bin' >> /etc/bash.bashrc
#RUN echo 'export PYTHONPATH=/usr/lib/pymodules/python2.7:$PYTHONPATH' >> /etc/bash.bashrc
#RUN echo 'export LD_LIBRARY_PATH=/usr/share/java:/usr/lib:$LD_LIBRARY_PATH' >> /etc/bash.bashrc

# PostgreSQL
USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER db_user WITH PASSWORD 'omx';" &&\
    createdb -O db_user omero_database

USER omero
WORKDIR /opt/omero/OMERO.server
RUN mkdir /tmp/omero
ENV OMERO_TEMPDIR /tmp/omero
RUN bin/omero config set omero.db.name 'omero_database' &&\
    bin/omero config set omero.db.user 'db_user' &&\
    bin/omero config set omero.db.pass 'omx'
RUN mkdir /opt/omero/OMERO.data
RUN bin/omero config set omero.data.dir /opt/omero/OMERO.data
RUN echo -e "" | bin/omero db script OMERO4.4 0 omx
#RUN psql -U db_user omero_database < OMERO4.4__0.sql
