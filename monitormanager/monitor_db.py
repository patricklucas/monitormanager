from __future__ import absolute_import

from collections import namedtuple
import logging
import time

import boto.dynamodb2
from boto.dynamodb2.exceptions import ItemNotFound
from boto.dynamodb2.table import Table
import simplejson as json

from monitormanager.monitor_config import parse_monitor_config
from monitormanager.monitor_config import MonitorConfigParseError

log = logging.getLogger(__name__)

DYNAMODB_REGION = 'us-west-1'
DYNAMODB_MONITORS_TABLE = 'monitormanager_monitors'
DYNAMODB_CONFIGS_TABLE = 'monitormanager_configs'

Monitor = namedtuple('Monitor', "identity alias config")


class MonitorDB(object):

    _dynamodb = None
    _monitors_table = None
    _configs_table = None

    @property
    def dynamodb(self):
        if self._dynamodb is None:
            self._dynamodb = boto.dynamodb2.connect_to_region(DYNAMODB_REGION)

        return self._dynamodb

    @property
    def monitors_table(self):
        if self._monitors_table is None:
            self._monitors_table = Table(DYNAMODB_MONITORS_TABLE,
                                         connection=self.dynamodb)

        return self._monitors_table

    @property
    def configs_table(self):
        if self._configs_table is None:
            self._configs_table = Table(DYNAMODB_CONFIGS_TABLE,
                                        connection=self.dynamodb)

        return self._configs_table

    def get_active_monitors(self):
        result_set = self.monitors_table.scan()

        monitors = []
        for result in result_set:
            identity = result['identity']
            alias = result['alias']
            config = self._get_current_config(identity)
            monitors.append(Monitor(identity, alias, config))

        return monitors

    def get_monitor(self, identity):
        try:
            item = self.monitors_table.get_item(identity=identity)
        except ItemNotFound:
            return None

        alias = item['alias']
        config = self._get_current_config(identity)

        return Monitor(identity, alias, config)

    def _parse_monitor_config_dict(self, monitor_config):
        try:
            return json.loads(monitor_config)
        except TypeError:
            return None

    def _get_current_config(self, identity):
        result_set = self.configs_table.query_2(
            identity__eq=identity,
            limit=1,
            reverse=True,
        )

        items = list(result_set)
        if not items:
            return None

        monitor_config_dict = self._parse_monitor_config_dict(
            items[0]['monitor_config'])
        if not monitor_config_dict:
            return None

        try:
            return parse_monitor_config(monitor_config_dict)
        except MonitorConfigParseError:
            log.warn("Ignoring invalid current config for '%s'", identity,
                     exc_info=True)
            return None

    def get_previous_10_configs(self, identity):
        result_set = self.configs_table.query_2(
            identity__eq=identity,
            limit=11,
            reverse=True,
        )

        configs = []
        for result in result_set:
            monitor_config_dict = self._parse_monitor_config_dict(
                result['monitor_config'])
            if not monitor_config_dict:
                continue

            try:
                configs.append(parse_monitor_config(monitor_config_dict))
            except MonitorConfigParseError:
                continue

        return configs[1:]

    def set_monitor(self, monitor):
        current_config = self._get_current_config(monitor.identity)

        if monitor.config != current_config:
            self.configs_table.put_item(data={
                'identity': monitor.identity,
                'timestamp': time.time(),
                'monitor_config': json.dumps(monitor.config.as_dict()),
            })

        item = self.ensure_monitor_exists(monitor.identity)
        item['alias'] = monitor.alias
        item.save()

    def ensure_monitor_exists(self, identity):
        try:
            item = self.monitors_table.get_item(identity=identity)
        except ItemNotFound:
            item = self.monitors_table.put_item(data={
                'identity': identity,
            })

        return item
