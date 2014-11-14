import sys

from setuptools import setup

from monitormanager import __version__


extra_install_requires = []
if sys.version_info < (2, 7):
    # argparse is in the standard library of Python >= 2.7
    extra_install_requires.append("argparse")

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
    ] + extra_install_requires,
)
