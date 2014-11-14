#!/bin/bash

mkdir /root/monitormanager-copy
pushd /root/monitormanager-copy
git -C /root/monitormanager archive HEAD | tar -x
yes | mk-build-deps -ri
dpkg-buildpackage -us -uc
popd

mv /root/*.deb /root/dist/
