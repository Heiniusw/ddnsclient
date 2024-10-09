import requests
import logging

logger = logging.getLogger(__name__)

def send_cloudflare_request(ipv4, ipv6_prefix, config):
    url = f"https://api.cloudflare.com/client/v4/zones/{config['zone_id']}/dns_records/"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": config['api_email'],
        "X-Auth-Key": config['api_key']
    }
    payload = {
        "name": config['name'],
        "proxied": True,
        "settings": {},
        "tags": [],
        "ttl": 3600
    }

    def send_request(ip, type, url, dns_record_id):
        url += dns_record_id
        payload.update({
            "content": ip,
            "type": type
        })
        logger.debug(f"Sending Request: {url}, Payload = {payload}, Headers = {headers}")
        try:
            response = requests.request("PUT", url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Response for {config['dns_record_id']} type {type}: {response.text.strip()}")
        except requests.RequestException as e:
            logger.error(f"Failed to update {config['dns_record_id']} type {type}: {str(e)}")

    if ipv4:
        send_request(ipv4, 'A', url, config['dns_record_id_ipv4'])
    
    if ipv6_prefix:
        send_request(ipv6_prefix, 'AAAA', url, config['dns_record_id_ipv6'])

def send_dyndns2_request(ipv4, ipv6_prefix, config):
    for domain in config['domains']:
        ipv6 = None
        if 'ipv6_suffix' in domain and domain['ipv6_suffix']:
            ipv6 = ipv6_prefix + ":" + domain['ipv6_suffix'] if ipv6_prefix else None

        ips = []
        if ipv4:
            ips.append(ipv4)
        if ipv6:
            ips.append(ipv6)
        
        url = f"https://{config['provider_host']}?hostname={domain['hostname']}&myip={','.join(ips)}"

        logger.debug(f"Sending Request: {url}")
        try:
            response = requests.get(url, auth=(config['username'], config['password']))
            response.raise_for_status()
            logger.info(f"Response for {domain['hostname']}: {response.text.strip()}")
        except requests.RequestException as e:
            logger.error(f"Failed to update {domain['hostname']}: {str(e)}")

def handle_request(ipv4, ipv6_prefix, provider, config):
    handlers = {"dyndnsv2": send_dyndns2_request, "cloudflare": send_cloudflare_request}
    handlers[provider](ipv4, ipv6_prefix, config)
