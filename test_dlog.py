import logging
import os
import sys
import time

from rdb import DistributedHandler, extendLogger, dlogReceiver

PORT = 8000
HOST = 'http://localhost:{0}/log/'.format(PORT)

if len(sys.argv) > 1:
    dlogReceiver(PORT)

os.system('python {0} 1 &'.format(os.path.realpath(__file__)))
time.sleep(0.25)

logger = logging.getLogger('foo')
logger.addHandler(DistributedHandler(HOST))
extendLogger(logger)
logger.setLevel(logging.DEBUG)

logger.debug('foo')
logger.info('foo')
logger.warn('foo')
logger.error('foo')

data = {
    'a': range(10),
    'b': [chr(i + ord('A')) for i in range(26)]
}
logger.pprint(data)

def f():
    logger.stack()

def g():
    f()

g()

os.system('ps ax | grep test_dlog.py | cut -c -6 | xargs kill -9')
