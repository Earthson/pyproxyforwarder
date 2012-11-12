#!/usr/bin/env python

import sys
import socket
from threading import Thread
from queue import Queue

proxy_queue = Queue()

def read_proxys(filename):
    ff = open(filename, 'r')
    addrs = [each.split(':') for each in ff]
    for each in addrs:
        for i in range(30):
            proxy_queue.put((each[0], int(each[1])))
    ff.close()

def random_proxy():
    print('#current proxy pool', proxy_queue.qsize())
    return proxy_queue.get()

def return_proxy(addr):
    proxy_queue.put(addr)

def data_forward_func(conn0, conn1):
    def func():
        try:
            while True:
                data = conn0.recv(1024)
                conn1.send(data)
        except socket.error as e:
            print(e, file=sys.stderr)
        except IOError as e:
            print('##', e, file=sys.stderr)
    return func

def start_forwarder(conn, addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    proxy_addr = random_proxy()
    s.connect(proxy_addr)
    print('#conn start')
    t1 = Thread(target=data_forward_func(conn, s))
    t1.start()
    t2 = Thread(target=data_forward_func(s, conn))
    t2.start()
    t1.join()
    t2.join()
    print('##conn end')
    return_proxy(proxy_addr)

def start_server(addr, ipv6=False):
    sock_s = socket.socket(socket.AF_INET if not ipv6 else socket.AF_INET6, 
                socket.SOCK_STREAM)
    print(addr)
    sock_s.bind(addr)
    sock_s.listen(128)
    while True:
        conn, addr = sock_s.accept()
        conn.settimeout(5)
        ff = Thread(target=lambda:start_forwarder(conn, addr))
        ff.setDaemon(True)
        ff.start()

if __name__ == '__main__':
    read_proxys('proxy.conf')
    start_server(('localhost', 9999))
