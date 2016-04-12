import os
import smtplib
import socket
import sys
import threading
import remote_pdb


_email = """From: {0}\r
To: {1}\r
Subject: Opening remote PDB telnet session\r
\r
Run:  telnet <ipaddr> {2}\r
where ipaddr is one of these: {3}\r
\r
PDB commands: https://docs.python.org/2/library/pdb.html#debugger-commands\r
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


class EmailNotifier(threading.Thread):
    def __init__(self, smtp_server, sender, recipients, port):
        threading.Thread.__init__(self)
        self._smtp_server = smtp_server
        self._sender = sender
        self._recipients = recipients
        self._port = port

    def run(self):
        try:
            server = smtplib.SMTP(self._smtp_server)
            server.sendmail(
                self._sender,
                self._recipients,
                _email.format(
                    self._sender,
                    ", ".join(self._recipients),
                    self._port,
                    get_ip_addresses()
                )
            )
            server.quit()
        except:
            pass


class RemotePdb(remote_pdb.RemotePdb):

    def __init__(self, host='0.0.0.0', port=4444,
                 smtp_server=None, sender=None, recipients=None,
                 patch_stdstreams=False):
        self._host = host
        self._port = port
        notifier = None
        if smtp_server and sender and recipients:
            notifier = EmailNotifier(smtp_server, sender, recipients, port)
        self._notifier = notifier
        remote_pdb.RemotePdb.__init__(self, host, port, patch_stdstreams)

    def set_trace(self):
        if self._notifier:
            self._notifier.start()
        remote_pdb.RemotePdb.set_trace(self)

    # Be able to run shell commands
    def do_sh(self, *args):
        cmd = ' '.join(args)
        print >>self.stdout, os.popen(cmd).read().rstrip()
