from setuptools import setup

from monitormanager import __version__


setup(
    name="monitormanager",
    version=__version__,
    author="Patrick Lucas",
    author_email="me@patricklucas.com",
    description="Monitor manager!",
    packages=["monitormanager"],
    package_data={"monitormanager": ["static/*", "templates/*"]},
    scripts=["scripts/monitormanager-server", "scripts/monitormanager-client"],
    install_requires=[
        "Flask",
        "boto",
        "gevent",
        "kazoo",
        "simplejson",
        "PyStaticConfiguration",
        "PyYAML",
    ],
)
