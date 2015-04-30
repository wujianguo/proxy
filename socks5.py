#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if sys.version_info < (2, 6):
    import simplejson as json
else:
    import json

try:
    import gevent
    import gevent.monkey
    gevent.monkey.patch_all(dns=gevent.version_info[0] >= 1)
except ImportError:
    gevent = None

import socket
import select
import SocketServer
import struct
import os
import logging
import StringIO
import urllib
import subprocess

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

class Socks5Server(SocketServer.StreamRequestHandler):

    def send_all(self, sock, data):
        bytes_sent = 0
        while True:
            r = sock.send(data[bytes_sent:])
            if r < 0:
                return r
            bytes_sent += r
            if bytes_sent == len(data):
                return bytes_sent

    def handle_tcp(self, sock, remote):
        try:
            fdset = [sock, remote]
            while True:
                r, w, e = select.select(fdset, [], [])
                if sock in r:
                    data = sock.recv(4096)
                    if len(data) <= 0:
                        break
                    result = self.send_all(remote, data)
                    if result < len(data):
                        raise Exception('failed to send all data')

                if remote in r:
                    data = remote.recv(4096)
                    if len(data) <= 0:
                        break
                    result = self.send_all(sock, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
        finally:
            sock.close()
            remote.close()

    def handle(self):
        sock = self.connection
        data = sock.recv(262)
        sock.send("\x05\x00")
        data = self.rfile.read(4) or '\x00' * 4
        mode = ord(data[1])
        if mode != 1:
            logging.warn('mode != 1')
            return

        addrtype = ord(data[3])
        if addrtype == 1:
            remote_addr = socket.inet_ntoa(self.rfile.read(4))
        elif addrtype == 3:
            addr_len = self.rfile.read(1)
            remote_addr = self.rfile.read(ord(addr_len))
        elif addrtype == 4:
            remote_addr = socket.inet_ntoa(self.rfile.read(16))
        else:
            logging.warn('addr_type not support:%d' % addrtype)
            return
        remote_port = struct.unpack('>H', self.rfile.read(2))[0]
        try:
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            remote.connect((remote_addr, remote_port))
            logging.info('connecting %s:%d' % (remote_addr, remote_port))
        except socket.error, e:
            logging.warn(e)
            return
        reply = "\x05\x00\x00\x01"
        reply += socket.inet_aton('0.0.0.0') + struct.pack(">H", 2222)
        self.wfile.write(reply)
        self.handle_tcp(sock, remote)

def main():
    # root_dir = sys.path[0]
    # if not os.path.isdir(root_dir):
    #     root_dir = os.path.split(root_dir)[0]
    # os.chdir(root_dir)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(lineno)d %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')
    logging.debug('0.0.0.0:1080  serving...')
    server = ThreadingTCPServer(('0.0.0.0', 1080), Socks5Server)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.warn('KeyboardInterrupt')
    finally:
        server.shutdown()
        logging.debug('done')


if __name__ == '__main__':
    main()
