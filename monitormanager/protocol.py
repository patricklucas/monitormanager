from collections import namedtuple

import simplejson as json

from monitormanager.monitor_config import parse_monitor_config

Command = namedtuple('Command', "cmd cmd_data")
ConfigUpdate = namedtuple('ConfigUpdate', "monitor_config")
Action = namedtuple('Action', "action_type params")
Heartbeat = namedtuple('Heartbeat', "")


def serialize_identity(identity):
    payload = {'identity': identity}
    data = json.dumps(payload)
    return data + '\n'


def deserialize_identity(data):
    payload = json.loads(data)
    identity = payload['identity']
    return identity


def serialize_command(command):
    payload = {
        'cmd': command.cmd,
        'cmd_data': command.cmd_data,
    }
    data = json.dumps(payload)
    return data + '\n'


def deserialize_command(data):
    payload = json.loads(data)
    command = Command(payload['cmd'], payload['cmd_data'])

    if command.cmd == 'config_update':
        monitor_config_dict = command.cmd_data['monitor_config']
        monitor_config = parse_monitor_config(monitor_config_dict)
        return ConfigUpdate(monitor_config)
    elif command.cmd == 'action':
        action_type = command.cmd_data['action_type']
        params = command.cmd_data['params']
        return Action(action_type, params)
    elif command.cmd == 'heartbeat':
        return Heartbeat()

    assert False, "unknown command"


def serialize_config_update(config_update):
    if not isinstance(config_update, ConfigUpdate):
        raise TypeError("'config_update' must be of type %r" % ConfigUpdate)

    command = Command('config_update', {
        'monitor_config': config_update.monitor_config.as_dict(),
    })
    return serialize_command(command)


def serialize_action(action):
    if not isinstance(action, Action):
        raise TypeError("'action' must be of type %r" % Action)

    command = Command('action', {
        'action_type': action.action_type,
        'params': action.params,
    })
    return serialize_command(command)


def serialize_heartbeat():
    command = Command('heartbeat', None)
    return serialize_command(command)
