#! /bin/bash

iface="eth0"

ip -6 a show dev $iface scope global | grep "inet6 200" | grep -v "deprecated" | cut -d' ' -f6 | cut -d':' -f1-4 | head -n 1
