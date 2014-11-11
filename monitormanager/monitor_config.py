from collections import namedtuple

MODE_SINGLE_URL = 0


class MonitorConfigParseError(Exception):
    pass


class MonitorConfig(namedtuple('MonitorConfig', "mode params")):

    def __new__(cls, params):
        mode = cls.MODE
        return super(MonitorConfig, cls).__new__(cls, mode, params)

    @classmethod
    def create(cls, *args, **kwargs):
        mode = cls.MODE
        params = cls.get_params(*args, **kwargs)
        return super(MonitorConfig, cls).__new__(cls, mode, params)

    def as_dict(self):
        return {
            'mode': self.MODE,
            'params': self.params,
        }


class SingleURLMonitorConfig(MonitorConfig):

    MODE = MODE_SINGLE_URL

    @classmethod
    def get_params(cls, url):
        return {
            'url': url,
        }

    @property
    def url(self):
        return self.params['url']


MONITOR_CLASSES = {
    MODE_SINGLE_URL: SingleURLMonitorConfig,
}


def parse_monitor_config(monitor_config_dict):
    mode = monitor_config_dict['mode']
    params = monitor_config_dict['params']

    cls = MONITOR_CLASSES.get(mode)
    if not cls:
        raise MonitorConfigParseError("Unknown monitor config mode: %r" % mode)

    return cls(params)
