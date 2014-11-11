from __future__ import absolute_import

from collections import defaultdict
import logging

import gevent

log = logging.getLogger(__name__)


class Switchboard(object):

    def __init__(self):
        self.clients = defaultdict(set)

    def register(self, identity, client):
        self.clients[identity].add(client)

    def deregister(self, identity, client):
        self.clients[identity].remove(client)

    def send_config_update(self, identity, config):
        for client in set(self.clients[identity]):
            client.send_config_update(config)

    def send_action(self, identity, action_type, params):
        for client in set(self.clients[identity]):
            client.send_action(action_type, params)

    def send_heartbeat(self):
        for clients in self.clients.values():
            for client in set(clients):
                client.send_heartbeat()

    def heartbeat(self):
        """periodically send a heartbeat to all clients"""
        while True:
            gevent.sleep(60)
            self.send_heartbeat()
