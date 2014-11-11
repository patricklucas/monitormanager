from __future__ import absolute_import

import logging
import sys

import gevent

from monitormanager.browser import Browser
from monitormanager.client_conn import ClientConn

log = logging.getLogger(__name__)


class Client(object):

    def __init__(self, identity, server_addr):
        self.identity = identity
        self.client_conn = ClientConn(identity, server_addr, self.on_data)

    def start(self):
        self.client_conn_greenlet = gevent.Greenlet(self.client_conn.run)
        self.client_conn_greenlet.link_exception(self.on_client_conn_exception)
        self.client_conn_greenlet.start()

    def on_data(self, data):
        log.info("got data: %r", data)

    def on_client_conn_exception(self, *args, **kwargs):
        log.exception("got client_conn exception")
        sys.exit(1)

    def join(self):
        return self.client_conn_greenlet.join()


def main():
    identity = sys.argv[1]
    client = Client(identity, ("localhost", 8765))
    client.start()
    client.join()

    #browser = Browser()
    #with browser:
    #    send_config(browser)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
