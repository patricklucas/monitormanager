from __future__ import absolute_import

import logging
import os

import gevent
from gevent.pywsgi import WSGIServer
from gevent.server import StreamServer

from monitormanager.config import config
from monitormanager.monitor_db import MonitorDB
from monitormanager.http_server import app
from monitormanager.server_client import ServerClient
from monitormanager.switchboard import Switchboard

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


def main():
    if os.path.isfile("config.yaml"):
        config.load("config.yaml")

    monitor_store = MonitorDB()
    app.monitor_store = monitor_store

    switchboard = Switchboard()
    app.switchboard = switchboard
    switchboard_greenlet = gevent.spawn(switchboard.heartbeat)

    server_addr = (config.mm_listen_host, config.mm_listen_port)
    server = Server(server_addr, monitor_store, switchboard)
    server_greenlet = gevent.spawn(server.serve_forever)

    http_server_addr = (config.http_listen_host, config.http_listen_port)
    http_server = WSGIServer(http_server_addr, app)
    http_server_greenlet = gevent.spawn(http_server.serve_forever)

    gevent.joinall([
        switchboard_greenlet,
        server_greenlet,
        http_server_greenlet
    ])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
