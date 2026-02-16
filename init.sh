#!/bin/sh
nohup python3 /whois-server.py &
nohup /usr/sbin/named -4 -g -c /etc/bind/named.conf &
sleep infinity
