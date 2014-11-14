from __future__ import absolute_import

import argparse
import logging
import os

import gevent
from gevent.pywsgi import WSGIServer

from monitormanager import __version__
from monitormanager.client import Client
from monitormanager.config import config
from monitormanager.http_server import app
from monitormanager.monitor_db import MonitorDB
from monitormanager.server import Server
from monitormanager.switchboard import Switchboard

DEFAULT_CONFIG_FILE = "config.yaml"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Monitor manager",
        add_help=False)
    parser.add_argument(
        "-h", "--help", action="help",
        help="Show this message and exit")
    parser.add_argument(
        "-c", "--config", dest="config_file",
        default=None,
        help="Path to configuration file (default: %s)" % DEFAULT_CONFIG_FILE)
    parser.add_argument(
        "-v", "--verbose", dest="verbose",
        default=False, action="store_true",
        help="Verbose output")
    parser.add_argument(
        "--version", action="version",
        version="%(prog)s {0}".format(__version__),
        help="Show version number and exit")

    return parser.parse_args()


def configure_logging(args):
    if args.verbose:
        level = logging.INFO
    else:
        level = logging.WARN

    logging.basicConfig(level=level)


def load_config(args):
    if args.config_file is None:
        if os.path.isfile(DEFAULT_CONFIG_FILE):
            config.load(DEFAULT_CONFIG_FILE)
    elif args.config_file:
        config.load(args.config_file)


def common_init():
    args = parse_args()
    configure_logging(args)
    load_config(args)


def run_server():
    common_init()

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


def run_client():
    common_init()

    client_addr = (config.mm_connect_host, config.mm_connect_port)
    client = Client(config.identity, client_addr)
    client.start()
    client.join()

    #browser = Browser()
    #with browser:
    #    send_config(browser)
