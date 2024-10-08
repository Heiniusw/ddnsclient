# ddnsclient
A ipv4 and ipv6 DynDNS client for multiple Hosts.

It takes the current ipv4 address from ipv4.sh and the current ipv6 prefix from ipv6_prefix.sh. If it detects a change of a ip compared to the cache it updates the ips.

## Install Packages
`pip install -r requirements.txt`
oder
`sudo apt install python3-full python3-filelock`

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
    "version": "1",
    "log_file": "/var/log/ddnsclient/ddns_update.log",
    "logging_level": "INFO",
    "modules": {
        "ipv4": {
            "command": "bash",
            "script": "./modules/ipv4-fritzbox.sh"
        },
        "ipv6": {
            "command": "bash",
            "script": "./modules/ipv6_prefix.sh"
        }
    },
    "providers": [
        {
            "providerHost": "dyndns.host.com/nic/update",
            "username": "example.com",
            "password": "abcdefg",
            "domains": [
                {
                    "hostname": "example.com",
                    "ipv6_suffix": "abcd:efab:cdef:abcd"
                },
                {
                    "hostname": "sub.example.com",
                    "ipv6_suffix": "1234:5678:9012:3456"
                },
                {
                    "hostname": "affe.example.com"
                }
            ]
        },
        {
            "providerHost": "dyndns.host2.com/nic/update",
            "username": "example.net",
            "password": "1234567890",
            "domains": [
                {
                    "hostname": "example.net",
                    "ipv6_suffix": "1234:4321:1234:4321"
                }
            ]
        }
    ]
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
