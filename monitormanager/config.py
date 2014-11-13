import staticconf
from staticconf import schema

NAMESPACE = "monitormanager"


class Config(schema.Schema):

    namespace = NAMESPACE

    # Server
    mm_listen_host = schema.string(default="0.0.0.0")
    mm_listen_port = schema.int(default=8765)
    http_listen_host = schema.string(default="0.0.0.0")
    http_listen_port = schema.int(default=8766)

    # Client
    mm_connect_host = schema.string(default="127.0.0.1")
    mm_connect_port = schema.int(default=8765)

    # AWS
    aws_region = schema.string(default="us-west-1")
    dynamodb_monitors_table = schema.string(default="monitormanager_monitors")
    dynamodb_configs_table = schema.string(default="monitormanager_configs")

    def load(self, path):
        staticconf.YamlConfiguration(path, namespace=NAMESPACE,
                                     error_on_unknown=True)

    def update(self, key, value):
        staticconf.DictConfiguration(dict([(key, value)]), namespace=NAMESPACE)


config = Config()
