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
`config.json`
### Logging Levels
DEBUG INFO WARNING ERROR CRITICAL

### Modules
IPv4 und IPv6. Remove to disable the Version. Requires a Command and a Script path.

### Providers
A Array of DynDNS Providers with its Hostname, Username and Password.
It also contains a list of Domains wich should be updated. A Hostname is required and the IPv6 Suffix is optional.

### Templates
#### Linux
```json:
{
    "version": "1",
    "log_file": "/var/log/ddnsclient/ddns_update.log",
    "logging_level": "INFO",
    "log_rotation": true,
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
    "providers": {
        "dyndnsv2": {
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
        "cloudflare": {
            "zone_id": "023e105f4ecef8ad9ca31a8372d0c353",
            "dns_record_id_ipv4": "023e105f4ecef8ad9ca31a8372d0c353",
            "dns_record_id_ipv6": "023e105f4ecef8ad9ca31a8372d0c353",
            "api_email": "max.musterman@example.com",
            "api_key": "123abc",
            "name": "example.com",
            "ipv6_suffix": "1234:4321:1234:4321"
        }
    }
}
```
#### Windows
```json:
{
    "version": "1",
    "log_file": "C:\\TEMP\\ddns_update.log",
    "logging_level": "INFO",
    "log_rotation": true,
    "modules": {
        "ipv4": {
            "command": "powershell",
            "args": ["-ExecutionPolicy", "Bypass", "-File", "./modules/ipv4-fritzbox.sh"]
        },
        "ipv6": {
            "command": "powershell",
            "args": ["-ExecutionPolicy", "Bypass", "-File", "./modules/ipv6_prefix.sh"]
        }
    },
    "providers": {
        "dyndnsv2": {
            "providerHost": "dyndns.host.com/nic/update",
            "username": "example.com",
            "password": "abcdefg",
            "domains": [
                {
                    "hostname": "example.com",
                    "ipv6_suffix": "abcd:efab:cdef:abcd"
                }
            ]
        }
    }
}
```

## Logs
For Rotation set "log_rotation" to true or use Logrotate from Linux.
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
