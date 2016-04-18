#!/usr/bin/env python

import httplib
import json
import logging
import requests
from werkzeug.exceptions import abort
from flask import Flask, request, render_template, send_from_directory, url_for
app = Flask(__name__)

logging.basicConfig(filename='/shared/listener.log', level=logging.DEBUG)

logs = []

def get_addresses():
    d = {}
    for line in open('/shared/addresses').readlines():
        host, addr = line.strip().split('=')
        d[host] = addr
    return d

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/images/<path:path>')
def show_image(path):
    return open('static/' + path).read()

def jtable(x):
    return json.dumps(
        dict(data=x),
        sort_keys=True,
        indent=4, separators=(',', ': ')
    )

@app.route('/get_logs')
def get_logs():
    return jtable(logs)


@app.route('/log', methods = ['POST'])
def post_log():
    log = {
        'ipaddr': request.form['ipaddr'],
        'levelname': request.form['levelname'],
        'pathname': request.form['pathname'],
        'lineno': request.form['lineno'],
        'funcName': request.form['funcName'],
        'exc_info': request.form['exc_info'],
        'msg': request.form['msg'],
        'created': request.form['created']
    }
    logs.append(log)
    return ''

@app.route('/rdb', methods = ['POST'])
def post_rdb():
    logging.info(request.form)
    return ''

if __name__ == '__main__':
    app.run('0.0.0.0')
