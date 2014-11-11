from __future__ import absolute_import

import logging

from gevent import Timeout, socket

from monitormanager import protocol

log = logging.getLogger(__name__)


class ServerClient(object):

    identity = None

    def __init__(self, sock, monitor_store, switchboard):
        self.sock = sock
        self._peer = sock.getpeername()
        self.monitor_store = monitor_store
        self.switchboard = switchboard

    def run(self):
        log.info("client connected (%r)", self)

        self.identity = self._read_identity()
        if not self.identity:
            log.warn("client failed to ident; disconnecting (%r)", self)
            return

        log.info("client ident (%r)", self)

        self.monitor_store.ensure_monitor_exists(self.identity)

        self.switchboard.register(self.identity, self)
        monitor = self.monitor_store.get_monitor(self.identity)
        if monitor.config:
            self.send_config_update(monitor.config)

    def send_config_update(self, config):
        config_update = protocol.ConfigUpdate(config)
        data = protocol.serialize_config_update(config_update)
        self._send(data)

    def send_action(self, action_type, params):
        action = protocol.Action(action_type, params)
        data = protocol.serialize_action(action)
        self._send(data)

    def send_heartbeat(self):
        data = protocol.serialize_heartbeat()
        self._send(data)

    def _send(self, data):
        try:
            self.sock.sendall(data)
        except socket.error:
            log.info("client disconnected (%r)", self)
            self.switchboard.deregister(self.identity, self)

    def _read_identity(self):
        sockfile = self.sock.makefile()

        line = None
        with Timeout(5, False):
            line = sockfile.readline()

        sockfile.close()

        if line is None:
            return None

        return protocol.deserialize_identity(line)

    def __repr__(self):
        return "<ServerClient identity=%s addr=%s>" % (self.identity,
                                                       self._peer)
