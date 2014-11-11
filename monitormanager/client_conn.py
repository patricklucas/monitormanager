from __future__ import absolute_import

import logging

import gevent
from gevent import socket

from monitormanager import protocol

log = logging.getLogger(__name__)


class ClientConn(object):

    def __init__(self, identity, server_addr, callback):
        self.identity = identity
        self.server_addr = server_addr
        self.callback = callback
        self.sock = None

        self.running = False
        self.connected = False

    def _connect(self):
        log.info("connecting")

        while True:
            try:
                self.sock = socket.create_connection(self.server_addr, timeout=5)
            except socket.error as e:
                log.warn("connection failed")
                gevent.sleep(1)
                log.info("retrying")
            else:
                break

        log.info("identifying")
        self.sock.sendall(protocol.serialize_identity(self.identity))

        log.info("connected")
        self.connected = True

    def run(self):
        if self.running:
            raise Exception("Already running")

        while True:
            if not self.connected:
                self._connect()

            try:
                data = self.sock.recv(4096)
            except socket.timeout:
                continue
            except socket.error:
                log.warn("lost connection")
                self.connected = False
                continue

            if not data:
                log.warn("got EOF")
                self.connected = False
                gevent.sleep(1)
                continue

            command = protocol.deserialize_command(data)
            self.callback(command)

        self.sock.close()
        self.connected = False
        self.running = False
