# ddnsclient
A ipv4 and ipv6 DynDNS client for multiple Hosts.

It takes the current ipv4 address from ipv4.sh and the current ipv6 prefix from ipv6-prefix.sh. If it detects a change of a ip compared to the cache it updates the ips.

## Example Crontab
Edit via crontab -e
```
* * * * *       cd /bin/ddnsclient && python /bin/ddnsclient/ddns_updater.py
@reboot         cd /bin/ddnsclient && python /bin/ddnsclient/ddns_updater.py
```
