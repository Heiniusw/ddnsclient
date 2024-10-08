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
LOGGING_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

def ensure_directory(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def configure_logging(log_file, logging_level_str):
    ensure_log_directory(log_file)
    logging_level = LOGGING_LEVELS.get(logging_level_str.upper(), logging.INFO)
    logging.basicConfig(
        filename=log_file,
        level=LOGGING_LEVEL,
        format='%(asctime)s - %(levelname)s > %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def read_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"File {filename} not found.")
        return {}

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

def get_external_ipv4(ipv4_script):
    try:
        return subprocess.check_output([ipv4_script]).decode().strip()
    except Exception as e:
        logging.error(f"Failed to get IPv4: {e}")
        return None

def get_ipv6_prefix(ipv6_prefix_script):
    try:
        return subprocess.check_output([ipv6_prefix_script]).decode().strip()
    except Exception as e:
        logging.error(f"Failed to get IPv6: {e}")
        return None

def update_domain(ipv4, ipv6_prefix, username, password, hosts):
    for hostname, suffix in hosts.items():
        ipv6 = ipv6_prefix + ":" + suffix if ipv6_prefix and suffix else None
        send_dyndns2_request(ipv4, ipv6, username, password, hostname)

def send_dyndns2_request(ipv4, ipv6, username, password, hostname):
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

    logging.info(hostname + ": " + response.strip())
    return response

def write_json(config, filename='config.ini'):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)

def update(config, ipv4, ipv6_prefix):
    logging.info("IP addresses have changed. Updating DynDNS2...")
    for username, data in config['domains'].items():
        update_domain(ipv4, ipv6_prefix, username, data['password'], data['hosts'])
    logging.info("DynDNS2 update successful.")

def main():
    # Read Config
    config = read_json(CONFIG_FILE)

    # Setup Logging
    log_file = config.get("log_file", "/var/log/ddnsclient/ddns_update.log")
    logging_level = config.get("logging_level", "INFO")
    configure_logging(log_file, logging_level)

    # Aquire Lock
    lock_file = acquire_lock()
    logging.debug("Lock Acquired")
    
    # Read Cache
    cache = read_json(CACHE_FILE)

    # Get Script Paths
    ipv4_script = config.get("ipv4_script", "")
    ipv6_prefix_script = config.get("ipv6_prefix_script", "")

    # Get Cached IPs
    current_ipv4 = cache.get("ipv4")
    current_ipv6_prefix = cache.get("ipv6_prefix")

    # Get Current IPs
    new_ipv4 = get_external_ipv4(ipv4_script) or None
    new_ipv6_prefix = get_ipv6_prefix(ipv6_prefix_script) or None

    # Debug
    logging.debug(f"Cache: IPv4 = {current_ipv4}, IPv6 = {current_ipv6_prefix}")
    logging.debug(f"New:   IPv4 = {new_ipv4}, IPv6 = {new_ipv6_prefix}")

    # Set IP to None if New and Cached match
    if new_ipv4 == current_ipv4:
        new_ipv4 = None
    if new_ipv6_prefix == current_ipv6_prefix:
        new_ipv6_prefix = None

    # Update IPs wich changed
    if new_ipv4 is None and new_ipv6_prefix is None:
        logging.debug("IPs are unchanged or None")
    elif not config:
        logging.warning("Config is empty or None")
    else:
        update(config, new_ipv4, new_ipv6_prefix)
        if new_ipv4:
            cache['ipv4'] = new_ipv4
        if new_ipv6_prefix:
            cache['ipv6_prefix'] = new_ipv6_prefix
        cache['last_set'] = str(datetime.now())
        write_json(cache, CACHE_FILE)
        logging.info("Saved Cache")

    release_lock(lock_file)

if __name__ == "__main__":
    main()
