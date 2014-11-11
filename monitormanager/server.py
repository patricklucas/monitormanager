from __future__ import absolute_import

import logging

import gevent
from gevent.pywsgi import WSGIServer
from gevent.server import StreamServer

from monitormanager.monitor_db import MonitorDB
from monitormanager.http_server import app
from monitormanager.server_client import ServerClient
from monitormanager.switchboard import Switchboard

log = logging.getLogger(__name__)


class Server(object):

    def __init__(self, monitor_store, switchboard):
        self.server = StreamServer(('localhost', 8765), self.handle)
        self.monitor_store = monitor_store
        self.switchboard = switchboard

    def serve_forever(self):
        return self.server.serve_forever()

    def handle(self, sock, _):
        server_client = ServerClient(sock, self.monitor_store, self.switchboard)
        gevent.spawn(server_client.run)


def main():
    monitor_store = MonitorDB()

    switchboard = Switchboard()
    switchboard_greenlet = gevent.spawn(switchboard.heartbeat)

    server = Server(monitor_store, switchboard)
    server_greenlet = gevent.spawn(server.serve_forever)

    app.monitor_store = monitor_store
    app.switchboard = switchboard
    http_server = WSGIServer(('', 8766), app)
    http_server_greenlet = gevent.spawn(http_server.serve_forever)

    gevent.joinall([server_greenlet, http_server_greenlet])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
