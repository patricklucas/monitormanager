FROM ubuntu:trusty
MAINTAINER me@patricklucas.com

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y git devscripts equivs
ADD build-deb.sh /root/build-deb.sh
