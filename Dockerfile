FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -q update
RUN apt-get -qy install build-essential python-pip cython
RUN apt-get -qy install texlive-full latexmk biber graphviz chktex dot2tex
RUN apt-get -qy install imagemagick python-opencv python-wand python-plastex
RUN apt-get -qy install python-jinja2
# replace imagemagick's policy with our own to enable PDF support
COPY misc/policy.xml /etc/ImageMagick-6/policy.xml
WORKDIR /data
