#!/usr/bin/env python

import sys
import socket
from threading import Thread
from queue import Queue
from time import sleep

proxy_queue = Queue()

socket.setdefaulttimeout(70)
#socket.setblocking(True)

def read_proxys(filename):
    ff = open(filename, 'r')
    addrs = [each.split(':') for each in ff if each[0] != '#']
    for i in range(4):
        for each in addrs:
            try:
                proxyinfo = socket.getaddrinfo(each[0], int(each[1]))
            except:
                continue
            if not proxyinfo:
                continue
            proxy_queue.put(proxyinfo[0])
    ff.close()

def random_proxy():
    print('#current proxy pool', proxy_queue.qsize())
    return proxy_queue.get()

def return_proxy(addr):
    proxy_queue.put(addr)
    print('#current proxy pool', proxy_queue.qsize())

def data_forward_func(conn0, conn1):
    def func():
        try:
            while True:
                data = conn0.recv(4096)
                if not data:
                    break
                totalsent = 0
                while totalsent < len(data):
                    sent = conn1.send(data[totalsent:])
                    if sent == 0:
                        raise RuntimeError("## socket connection broken")
                    totalsent += sent
        except socket.error as e:
            print('$$$#', e, file=sys.stderr)
        except IOError as e:
            print('$$$#', e, file=sys.stderr)
        except Exception as e:
            print(e)
    return func

def try_connect(addrinfo):
    print('#connect to:', addrinfo)
    s = socket.socket(family=addrinfo[0], type=addrinfo[1], proto=addrinfo[2])
    #s.setblocking(False)
    s.connect(addrinfo[4])
    return s

def start_forwarder(conn, addr):
    proxy_addr = random_proxy()
    try:
        s = try_connect(proxy_addr)
    except:
        print('#conn faild')
        sleep(0.1)
        try:
            s = try_connect(proxy_add)
        except:
            #return_proxy(proxy_addr)
            return False
    print('#conn start')
    t1 = Thread(target=data_forward_func(conn, s))
    t2 = Thread(target=data_forward_func(s, conn))
    t1.start()
    t2.start()
    while True:
        if t1.is_alive() and t2.is_alive():
            sleep(0.5)
        else:
            break
    try:
        s.close()
        conn.close()
    except Exception as e:
        print('#close error: ', e)
    print('##conn end')
    return_proxy(proxy_addr)
    return True

def start_server(addr, ipv6=False):
    sock_s = socket.socket(socket.AF_INET if not ipv6 else socket.AF_INET6, 
                socket.SOCK_STREAM)
    sock_s.settimeout(None)
    sock_s.bind(addr)
    sock_s.listen(256)
    while True:
        conn, addr = sock_s.accept()
        #conn.setblocking(False)
        ff = Thread(target=lambda:start_forwarder(conn, addr))
        ff.setDaemon(True)
        ff.start()

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except:
        port = 9999
    print('listen on: ', port)
    read_proxys('proxy.conf')
    start_server(('localhost', port))
