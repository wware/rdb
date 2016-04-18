import os
import sys
import remote_pdb

from .comms import get_host_ip, _local_ip


_email = """From: {0}\r
To: {1}\r
Subject: Opening remote PDB telnet session\r
\r
Run:  telnet <ipaddr> {2}\r
where ipaddr is one of these: {3}\r
\r
PDB commands: https://docs.python.org/2/library/pdb.html#debugger-commands\r
\r
{4}\r
"""


def get_ip_addresses():
    if sys.platform == 'cygwin':
        cmd = 'ipconfig | grep IPv4 | sed "s/.*: //"'
    else:
        cmd = (
            'ifconfig | grep "inet addr:.*Bcast" | ' +
            'sed "s/.*addr://" | sed "s/ .*//"'
        )
    return ", ".join([
        addr.strip() for addr in os.popen(cmd).readlines()
    ])


class RemotePdb(remote_pdb.RemotePdb):

    def __init__(self, port=4444, patch_stdstreams=False):
        self._port = port
        remote_pdb.RemotePdb.__init__(self, '0.0.0.0', port, patch_stdstreams)

    def set_trace(self):
        host_ip = get_host_ip()
        if host_ip is None:
            return
        my_ips = get_ip_addresses()
        try:
            params = urllib.urlencode(json.dumps(
                dict(ips=my_ips, port=self.port)
            ))
            headers = {"Content-type": "application/x-www-form-urlencoded",
                       "Accept": "text/plain"}
            conn = httplib.HTTPConnection(host_ip + ':5000')
            conn.request("POST", "/rdb", params, headers)
            conn.getresponse()
            conn.close()
        except:
            pass
        remote_pdb.RemotePdb.set_trace(self)

    # Be able to run shell commands
    def do_sh(self, *args):
        cmd = ' '.join(args)
        print >>self.stdout, os.popen(cmd).read().rstrip()
