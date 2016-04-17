import logging
from .rpdb import RemotePdb
import comms
from .dlog import DistributedHandler, extendLogger
from .digger import dig

_loggers = {}


def listener(get_host):
    _loggers.clear()
    comms._host_getter = get_host


def getLogger(name=''):
    logger = _loggers.get(name)
    if logger is not None:
        return logger
    # stifle almost all logging from werkzeug
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    logger = logging.getLogger(name)
    logger.addHandler(DistributedHandler())
    extendLogger(logger)
    _loggers[name] = logger
    return logger
