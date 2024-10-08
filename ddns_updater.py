from datetime import datetime
import json
import subprocess
import sys
from filelock import FileLock
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
    ensure_directory(log_file)
    logging_level = LOGGING_LEVELS.get(logging_level_str.upper(), logging.INFO)
    logging.basicConfig(
        filename=log_file,
        level=logging_level,
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
    lock = FileLock(LOCK_FILE)
    try:
        lock.acquire(timeout=1)
        return lock
    except Exception as e:
        logging.error(f"Failed to acquire lock: {e}")
        return None

def release_lock(lock):
    lock.release()

def execute_script(module):
    command = module.get("command")
    script = module.get("script")
    try:
        logging.debug(f"Executing script: {script} with command: {command}")
        return subprocess.check_output([command, script]).decode().strip()
    except Exception as e:
        logging.error(f"Failed to execute {script}: {e}")
        return None

def update(config, ipv4, ipv6_prefix):
    logging.info("IP addresses have changed. Updating DynDNS2...")
    for username, data in config['domains'].items():
        update_domain(ipv4, ipv6_prefix, username, data['password'], data['hosts'])
    logging.info("DynDNS2 update successful.")

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

def main():
    # Read Config
    config = read_json(CONFIG_FILE)
    if not config:
        logging.error(f"Invalid Config File: {CONFIG_FILE}")
        sys.exit()

    # Setup Logging
    log_file = config.get("log_file", "/var/log/ddnsclient/ddns_update.log")
    logging_level = config.get("logging_level", "INFO")
    configure_logging(log_file, logging_level)

    # Aquire Lock
    lock_file = acquire_lock()
    
    # Read Cache
    cache = read_json(CACHE_FILE)

    # Get Cached IPs
    current_ipv4 = cache.get("ipv4")
    current_ipv6_prefix = cache.get("ipv6_prefix")

    # Get Current IPs
    ipv4_module = config["modules"]["ipv4"]
    ipv6_prefix_module = config["modules"]["ipv6_prefix"]

    new_ipv4 = execute_script(ipv4_module) or None
    if not new_ipv4:
        logging.warning(f"IPv4 address is {new_ipv4}")
    new_ipv6_prefix = execute_script(ipv6_prefix_module) or None
    if not new_ipv6_prefix:
        logging.warning(f"IPv6 prefix is {new_ipv6_prefix}")

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
