"""
lircpy - A very simple python script for receiving commands from Lirc.
         By Weston Nielson <wnielson@github>.
"""
import logging
import socket
import re

from threading import Thread

class Handler(object):
    THROTTLE = 5
    REMOTE   = None

    def __call__(self, data):
        if self.REMOTE is not None and data['remote'] != self.REMOTE:
            return

        func = None
        if hasattr(self, data['key']):
            if self.THROTTLE > 0:
                try:
                    count = int(data['count'])
                    if count % self.THROTTLE != 0:
                        raise
                except:
                    return
            func = getattr(self, data['key'])
        elif hasattr(self, 'DEFAULT'):
            func = getattr(self, 'DEFAULT')

        if func is not None:
            func(data)

class Lirc(Thread):
    _RE = re.compile(r'^(?P<hex>[0-9a-f]+) (?P<count>[\da-f]+) (?P<key>[\S^ ]+) (?P<remote>[\S^ ]+)$')

    daemon = True

    def __init__(self, handler=Handler(), lircd='/dev/lircd'):
        self.lircd      = lircd
        self.handler    = handler
        self._sock      = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._stop      = False
        self._buf       = ''

        try:
            self._sock.connect(self.lircd)
            self._sock.settimeout(1)
        except Exception, e:
            logging.error("Error opening lircd: %s" % self.lircd)
            self._stop = True

        Thread.__init__(self)

        self.start()

    def stop(self):
        logging.info("Stopping Lirc...")
        self._stop = True

    def run(self):
        while not self._stop:
            try:
                self._buf += self._sock.recv(512, socket.MSG_DONTWAIT)
            except socket.timeout:
                continue
            except Exception, e:
                logging.error("Error with socket: %s" % e)
                self.stop()
                return

            if self._buf[-1] != '\n' or len(self._buf) == 1:
                continue

            # Copy and reset the buffer
            resp = self._buf
            self._buf = ''

            # Try to match the remote command
            match = self._RE.match(resp)
            if match:
                data = match.groupdict()
                if callable(self.handler):
                    self.handler(data)
            else:
                logging.error("Error matching lircd message: '%s'" % resp)
