from __future__ import absolute_import

import logging

import gevent
from gevent.server import StreamServer

from monitormanager.server_client import ServerClient

log = logging.getLogger(__name__)


class Server(object):

    def __init__(self, server_addr, monitor_store, switchboard):
        self.server = StreamServer(server_addr, self.handle)
        self.monitor_store = monitor_store
        self.switchboard = switchboard

    def serve_forever(self):
        return self.server.serve_forever()

    def handle(self, sock, _):
        server_client = ServerClient(sock, self.monitor_store,
                                     self.switchboard)
        gevent.spawn(server_client.run)
