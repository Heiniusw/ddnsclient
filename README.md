# ddnsclient
A ipv4 and ipv6 DynDNS client for multiple Hosts.

It takes the current ipv4 address from ipv4.sh and the current ipv6 prefix from ipv6_prefix.sh. If it detects a change of a ip compared to the cache it updates the ips.

## Example Crontab
Edit via crontab -e
```
* * * * *       cd /bin/ddnsclient && python /bin/ddnsclient/ddns_updater.py
@reboot         cd /bin/ddnsclient && python /bin/ddnsclient/ddns_updater.py
```

## Config
config.json
```json:
{
    "example.com": {
        "password": "abcdefg",
        "hosts": {
            "example.com": ":abcd:efab:cdef:abcd",
            "sub.example.com": ":1234:5678:9012:3456",
            "affe.example.com": ":affe:affe:affe:affe"
        }
    },
    "example.net": {
        "password": "1234567890",
        "hosts": {
            "example.net": ":1234:4321:1234:4321"
        }
    }
}
```

## Logs
Logfile: /var/log/ddnsclient/ddns_update.log
Logrotate config: /etc/logrotate.d/ddns_update
```
/var/log/ddnsclient/ddns_update.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```
