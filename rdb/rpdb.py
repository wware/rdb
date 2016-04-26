import httplib
import logging
import os
import sys
import threading
import urllib

import comms


def inform(host_ip, port):
    try:
        params = urllib.urlencode(
            {'ipaddr': comms._local_ip, 'port': port}
        )
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(host_ip + ':5000')
        conn.request("POST", "/rdb", params, headers)
        conn.getresponse()
        conn.close()
    except Exception as e:
        logging.exception(e)

