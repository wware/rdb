#!/usr/bin/env python

import datetime
import inspect
import json
import logging
import os
import random
import threading
import time

##########

def get_listener_ip_address():
    for line in open('/shared/addresses').readlines():
        host, addr = line.strip().split('=')
        if host == 'listener':
            return addr
    return None

import rdb
rdb.setup_comms("eth0", get_listener_ip_address)
logger = rdb.getLogger()
logger.setLevel(logging.DEBUG)

##########

from werkzeug.exceptions import abort
from flask import Flask
app = Flask(__name__)
app.debug = True

# logging.basicConfig(filename='/shared/worker.log', level=logging.DEBUG)
# logging.info('Log stuff from the worker')

jobs = {}
results = {}
workid = 1
lock = threading.Lock()
LOCK_DEBUG = False

def acq():
    if LOCK_DEBUG:
        stack = inspect.stack()
        frame = stack[1]
        logging.debug('%s:%d acquire lock' % frame[1:3])
    lock.acquire()

def rel():
    lock.release()
    if LOCK_DEBUG:
        stack = inspect.stack()
        frame = stack[1]
        logging.debug('%s:%d release lock' % frame[1:3])


class Job(threading.Thread):
    def __init__(self):
        global workid
        threading.Thread.__init__(self)

        acq()
        i = workid
        workid += 1
        jobs[str(i)] = self
        rel()

        self._id = i
        self._begin = t = datetime.datetime.now()
        self._duration = d = 5 + 5 * random.random()
        self._end = t + datetime.timedelta(seconds=d)

    def run(self):
        time.sleep(self._duration)
        i = self.id
        result = str(int(1000000 * random.random()))
        try:
            acq()
            results[i] = result
            del jobs[i]
        except Exception as e:
            logging.exception(e)
        finally:
            rel()

    @property
    def id(self):
        return str(self._id)

    @property
    def duration(self):
        return str(int(self._duration))

    @property
    def begin(self):
        return self._begin.strftime('%H:%M:%S')

    @property
    def end(self):
        return self._end.strftime('%H:%M:%S')

    @property
    def data(self):
        return dict(
            begin=self.begin,
            end=self.end,
            duration=self.duration,
            id=self.id
        )


def jdump(x):
    return json.dumps(x, sort_keys=True,
                      indent=4, separators=(',', ': '))


@app.route('/start')
def start():
    logger.info('start job')
    j = Job()
    j.start()
    return jdump(j.data)


@app.route('/status/<int:n>')
def status(n):
    try:
        acq()
        j = jobs.get(n)
        i = workid
    except Exception as e:
        logging.exception(e)
    finally:
        rel()
    if j is not None:
        data = j.data
        data['now'] = datetime.datetime.now().isoformat()
        return jdump(data)
    elif j < i:
        return 'done\n'
    else:
        abort(404)


@app.route('/result/<int:n>')
def result(n):
    try:
        acq()
        r = results.get(n)
    except Exception as e:
        logging.exception(e)
    finally:
        rel()
    if r is not None:
        return repr(r) + '\n'
    else:
        abort(404)


@app.route('/results')
def get_results():
    try:
        acq()
        r = results.items()
    except Exception as e:
        logging.exception(e)
    finally:
        rel()
    j = [{'id': u, 'result': v} for u, v in r]
    if j:
        logger.pprint(j)
    return jdump(j)


@app.route('/all')
def all():
    try:
        acq()
        all_jobs = [v.data for k, v in jobs.items()]
    except Exception as e:
        logging.exception(e)
    finally:
        rel()
    return jdump(all_jobs)


@app.route('/clear')
def clear():
    global workid
    try:
        acq()
        jobs.clear()
        results.clear()
        workid = 1
    except Exception as e:
        logging.exception(e)
    finally:
        rel()
    return ''


if __name__ == '__main__':
    app.run('0.0.0.0')