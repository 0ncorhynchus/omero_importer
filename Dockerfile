FROM ubuntu:12.04

RUN apt-get install -y wget unzip

RUN cd /tmp
RUN wget http://downloads.openmicroscopy.org/omero/4.4.8/OMERO.server-4.4.8-ice34-b256.zip
RUN unzip OMERO.server-4.4.8-iceb256.zip
