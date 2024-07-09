from datetime import datetime
import json
import subprocess
import sys
import fcntl
import os
import logging

CONFIG_FILE = "config.json"
CACHE_FILE = "cached_info.json"
LOCK_FILE = "ddns_updater.lock"
LOGGING_LEVEL = logging.INFO

# DEBUG INFO WARNING ERROR CRITICAL
logging.basicConfig(
        filename='/var/log/ddnsclient/ddns_update.log',
        level=LOGGING_LEVEL,
        format='%(asctime)s - %(levelname)s > %(message)s', datefmt="%Y-%m-%d %H:%M:%S"
    )

def acquire_lock():
    try:
        lock_file = open(LOCK_FILE, "w")
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        logging.error("Another instance of the script is running. Exiting.")
        sys.exit(1)

def release_lock(lock_file):
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
#    os.remove(LOCK_FILE)


# Function to get the current external IPv4 address
def get_external_ipv4():
    try:
        return subprocess.check_output(['./ipv4.sh']).decode().strip()
    except Exception as e:
        logging.error(f"Failed to get IPv4: {e}")
        return None

# Function to get the IPv6 prefix
def get_ipv6_prefix():
    try:
        return subprocess.check_output(['./ipv6_prefix.sh']).decode().strip()
    except Exception as e:
        logging.error(f"Failed to get IPv6: {e}")
        return None

def update_multiple(ipv4, ipv6_prefix, username, password, hosts):
    for hostname, suffix in hosts.items():
        ipv6 = ipv6_prefix + suffix if ipv6_prefix and suffix else None
        update_dyndns2(ipv4, ipv6, username, password, hostname)

# Function to update DynDNS2
def update_dyndns2(ipv4, ipv6, username, password, hostname):
    logging.debug(ipv4)
    logging.debug(ipv6)
    ips = ""
    if ipv4:
        ips = ipv4
    if ipv6:
        if ips:
            ips += "," + ipv6
        else:
            ips = ipv6
    url = f"https://{username}:{password}@dyndns.strato.com/nic/update?hostname={hostname}&myip={ips}"
    response = subprocess.check_output(['curl', '-s', url]).decode()
    #response = url

    logging.info(hostname + ": " + response.strip())
    return response

# Function to read configuration from file
def read_json(filename='config.ini'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Config file {filename} not found.")
        return {}

# Function to write configuration to file
def write_json(config, filename='config.ini'):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)

def update(config, ipv4, ipv6_prefix):
    logging.info("IP addresses have changed. Updating DynDNS2...")
    for username, data in config.items():
        update_multiple(ipv4, ipv6_prefix, username, data['password'], data['hosts'])
    logging.info("DynDNS2 update successful.")

# Main function
def main():
    lock_file = acquire_lock()
    logging.debug("Lock Aquired")
    config = read_json(CONFIG_FILE)
    cache = read_json(CACHE_FILE)

    current_ipv4 = cache.get("ipv4")
    current_ipv6_prefix = cache.get("ipv6_prefix")

    new_ipv4 = get_external_ipv4() or None
    new_ipv6_prefix = get_ipv6_prefix() or None

    logging.debug(f"Cache: IPv4 = {current_ipv4}, IPv6 = {current_ipv6_prefix}")
    logging.debug(f"New:   IPv4 = {new_ipv4}, IPv6 = {new_ipv6_prefix}")

    if new_ipv4 == current_ipv4:
        new_ipv4 = None
    if new_ipv6_prefix == current_ipv6_prefix:
        new_ipv6_prefix = None

    if new_ipv4 is None and new_ipv6_prefix is None:
        logging.debug("IPs are Unchanged or None")
    elif not config:
        logging.warning("Config is empty or None")
    else:
        update(config, new_ipv4, new_ipv6_prefix)
        if new_ipv4:
            cache['ipv4'] = new_ipv4
        if new_ipv6_prefix:
            cache['ipv6_prefix'] =  new_ipv6_prefix
        cache['last_set'] = str(datetime.now())
        write_json(cache, CACHE_FILE)
        logging.info("Saved Cache")


    #cache['last_checked'] = str(datetime.now())
    release_lock(lock_file)

if __name__ == "__main__":
    main()

