import logging
import pprint
import traceback
import socket
import time

from flask import Flask, request
import requests


def json_record(record):
    return {
        'levelname': record.levelname,
        'pathname': record.pathname,
        'lineno': record.lineno,
        'funcName': record.funcName,
        'exc_info': record.exc_info,
        'msg': record.msg,
        'created': record.created
    }


class DistributedHandler(logging.Handler):
    def __init__(self, uri):
        logging.Handler.__init__(self)
        self.uri = uri

    def emit(self, record):
        try:
            requests.post(self.uri, data=json_record(record))
        except requests.exceptions.ConnectionError:
            pass


def extendLogger(logger):
    def _pprint(thing, logger=logger):
        if logger.isEnabledFor(logging.INFO):
            logger._log(logging.INFO, pprint.pformat(thing), [])
    logger.pprint = _pprint

    def _stack(msg=None, logger=logger):
        if logger.isEnabledFor(logging.INFO):
            stuff = traceback.format_stack()[:-1]
            if msg is not None:
                stuff.append(str(msg))
            else:
                stuff[-1] = stuff[-1].rstrip()
            logger._log(logging.INFO, ''.join(stuff), [])
    logger.stack = _stack


def dlogReceiver(port=5000):
    # Stifle most Werkzeug output.
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app = Flask(__name__, static_url_path="")

    @app.route('/log/', methods=['POST'])
    def post():
        client = socket.gethostbyaddr(request.remote_addr)[0]
        print '{0} [{1}] <{2}> {3}:{4} {5}\n{6}\n'.format(
            client,
            request.form['levelname'],
            time.ctime(float(request.form['created'])),
            request.form['pathname'],
            request.form['lineno'],
            request.form['funcName'],
            request.form['msg']
            # exc_info????
        )
        return '', 200

    app.run(host="0.0.0.0", port=port, debug=True)
