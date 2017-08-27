#!/usr/bin/env python

import socket


#TCP_IP = '192.168.130.222'
TCP_IP = '172.16.0.127' #Server Icesi
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "AC 1 35.78"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()

print "received data:", data
