#! /bin/bash

ip -6 a show dev eth0 scope global | grep "inet6 200" | grep -v "deprecated" | cut -d' ' -f6 | cut -d':' -f1-4 | head -n 1
