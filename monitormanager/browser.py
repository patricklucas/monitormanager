from __future__ import absolute_import

import os
import socket
from subprocess import Popen
import time

UZBL_CMD = "/usr/bin/uzbl-browser"
SOCK_FMT = "/tmp/uzbl_socket_{0}"
URI_FILE = "/nail/etc/monitor-uri"


class Browser(object):

    p = None

    def __enter__(self):
        self.p = Popen([UZBL_CMD], stderr=open(os.devnull, 'w'))
        self.sock = self._wait_for_socket()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.p:
            self.p.terminate()
            self.p = None

        if self.sock:
            self.sock.close()
            self.sock = None

    @property
    def socket_filename(self):
        return SOCK_FMT.format(self.p.pid)

    def _wait_for_socket(self):
        while True:
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                sock.connect(self.socket_filename)
            except socket.error:
                time.sleep(.5)
            else:
                return sock

    def send_cmd(self, cmd):
        self.sock.sendall(cmd + '\n')


def read_uri():
    with open(URI_FILE) as f:
        return f.readlines()[0].strip()


def send_config(browser):
    browser.send_cmd("set uri={0}".format(read_uri()))
    browser.send_cmd("set show_status=0")
    browser.send_cmd("set geometry=maximized")


def handle_input(browser):
    while True:
        try:
            cmd = raw_input()
        except (KeyboardInterrupt, EOFError):
            break

        if not cmd:
            break

        browser.send_cmd(cmd)
