#!/bin/bash

mkdir /root/monitormanager-copy
rsync -a /root/monitormanager/ /root/monitormanager-copy/

pushd /root/monitormanager-copy
yes | mk-build-deps -ri
dpkg-buildpackage -us -uc
popd

mv /root/*.deb /root/dist/
