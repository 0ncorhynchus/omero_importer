FROM ubuntu:12.04

RUN apt-get install -y wget unzip
RUN cd /tmp; wget http://downloads.openmicroscopy.org/omero/4.4.8/OMERO.server-4.4.8-ice34-b256.zip
RUN cd /tmp; unzip OMERO.server-4.4.8-ice34-b256.zip
