from __future__ import print_function
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import pyrad.packet
from collections import OrderedDict
from pyrad.packet import AuthPacket, AccessRequest
import six
import random
import socket
import time
import argparse

class MyAuthPacket(AuthPacket):
    def __init__(self, code=AccessRequest, id=None, secret=six.b(''), authenticator=None, **attributes):
        self.attrs = OrderedDict()
        AuthPacket.__init__(self, code, id, secret,
                            authenticator, **attributes)

    def AddAttribute(self, key, item):
        if isinstance(key, six.string_types):
            (key, item) = self._EncodeKeyValues(key, [item])
            self.attrs[key] = item
        else:
            assert isinstance(item, list)
            self.attrs[key] = item

    def _PktEncodeAttributes(self):
        result = six.b('')
        for (code, datalst) in self.attrs.items():
            for data in datalst:
                result += self._PktEncodeAttribute(code, data)

        return result


def send_packet(server, port, secret, username, password, *attributes, source_port = None):
    req1 = MyAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username,
                        NAS_Identifier="localhost", dict=Dictionary("dictionary"))
    req1.secret = secret
    req1.authenticator = req1.CreateAuthenticator()

    req1.AddAttribute("User-Password", req1.PwCrypt(password))
    for (attr, value) in attributes:
        req1.AddAttribute(attr, value)

    data = req1.RequestPacket()


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if source_port is not None:
        sock.bind(("", source_port))

    sock.settimeout(1.0)

    sock.sendto(data, (server, port))
    try:
        data, addr = sock.recvfrom(1024)
        print(f"send to: {server:>15}:{port}     reply from: {addr[0]:>15}:{addr[1]}")
    except socket.timeout:
        print(f"send to: {server:>15}:{port}     reply timeout")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test FortiADC.')
    parser.add_argument('--vip', help='the ip of the radius vip', required=True)
    parser.add_argument('--rserver', help='rserver rip', required=True)
    parser.add_argument('--shared-secret', help='shared secret', required=True)
    parser.add_argument('--username', help='username', required=True)
    parser.add_argument('--password', help='password', required=True)
    parser.add_argument('--source-port', help='password', type=int, default=12345)
    
    args = parser.parse_args()

    vip = args.vip
    rserver = args.rserver
    shared_secret = args.shared_secret.encode()
    username = args.username.encode()
    password = args.password.encode()
    source_port = args.source_port

    mac = "AA-BB-CC-DD-01-%02d" % random.randint(0, 10)
    reply = send_packet(rserver, 1812, shared_secret, username, password, ('Calling-Station-Id', mac), source_port=source_port)
    time.sleep(1.0)
    reply = send_packet(vip, 1812, shared_secret, username, password, ('Calling-Station-Id', mac), source_port=source_port)
    time.sleep(1.0)
    repl = send_packet(rserver, 1812, shared_secret, username, password, ('Calling-Station-Id', mac), source_port=source_port)
