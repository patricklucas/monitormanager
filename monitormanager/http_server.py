from __future__ import absolute_import

import logging

from flask import Flask, redirect, request, url_for, abort, render_template

from monitormanager.monitor_config import SingleURLMonitorConfig
from monitormanager.monitor_db import Monitor

log = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def home():
    return redirect(url_for("list_monitors"))


@app.route("/monitors")
def list_monitors():
    monitors = app.monitor_store.get_active_monitors()
    return render_template("monitors.html", monitors=monitors)


@app.route("/monitor/<identity>", methods=['GET'])
def get_monitor(identity):
    monitor = app.monitor_store.get_monitor(identity)
    if not monitor:
        return abort(404)

    previous_10_configs = app.monitor_store.get_previous_10_configs(identity)

    return render_template("monitor.html",
                           monitor=monitor,
                           previous_10_configs=previous_10_configs)


@app.route("/monitor/<identity>", methods=['POST'])
def post_monitor(identity):
    if 'alias' not in request.form or 'url' not in request.form:
        return abort(400)

    alias = request.form['alias']
    url = request.form['url']
    config = SingleURLMonitorConfig.create(url)
    monitor = Monitor(identity, alias, config)

    app.monitor_store.set_monitor(monitor)
    app.switchboard.send_config_update(identity, config)

    return redirect(url_for("get_monitor", identity=identity))


@app.route("/monitor/<identity>/reload", methods=['POST'])
def reload_monitor(identity):
    app.switchboard.send_action(identity, 'reload', None)

    return redirect(url_for("get_monitor", identity=identity))
