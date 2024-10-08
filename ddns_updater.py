from datetime import datetime
import json
import subprocess
import sys
from filelock import FileLock
import os
import logging
from logging.handlers import RotatingFileHandler

CONFIG_FILE = "config.json"
CONFIG_VERSION = "1"
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

def configure_logging(log_file, logging_level_str, log_rotation=False):
    ensure_directory(log_file)
    logging_level = LOGGING_LEVELS.get(logging_level_str.upper(), logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s > %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    # Create a stream handler for stdout and add it
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging_level)
    stream_handler.setFormatter(formatter)
    logging.getLogger().addHandler(stream_handler)

    # If log_file is specified, also log to the file
    if log_file:
        if log_rotation:
            file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
        else:
            file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

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
    for provider in config['providers']:
        update_provider(ipv4, ipv6_prefix, provider['username'], provider['password'], provider['providerHost'], provider['domains'])
    logging.info("DynDNS update successful.")

def update_provider(ipv4, ipv6_prefix, username, password, provider_host, domains):
    for domain in domains:
        ipv6 = None
        if 'ipv6_suffix' in domain and domain['ipv6_suffix']:
            ipv6 = ipv6_prefix + ":" + domain['ipv6_suffix'] if ipv6_prefix else None

        send_dyndns2_request(ipv4, ipv6, username, password, provider_host, domain['hostname'])

def send_dyndns2_request(ipv4, ipv6, username, password, provider_host, hostname):
    ips = []
    if ipv4:
        ips.append(ipv4)
    if ipv6:
        ips.append(ipv6)
    
    url = f"https://{provider_host}?hostname={hostname}&myip={','.join(ips)}"
    logging.debug(f"Sending Request: {url}")
    
    try:
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()
        logging.info(f"Response for {hostname}: {response.text.strip()}")
    except requests.RequestException as e:
        logging.error(f"Failed to update {hostname}: {str(e)}")

def write_json(config, filename='config.ini'):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)

def main():
    # Read Config
    config = read_json(CONFIG_FILE)
    version = config.get("version", "unknown version")
    if not config:
        raise Exception(f"Invalid Config File: {CONFIG_FILE}")
    if version != CONFIG_VERSION:
        raise Exception(f"Config version mismatch: expected {CONFIG_VERSION}, got {version}")

    # Setup Logging
    log_file = config.get("log_file", "/var/log/ddnsclient/ddns_update.log")
    logging_level = config.get("logging_level", "INFO")
    log_rotation = config.get("log_rotation", False)
    configure_logging(log_file, logging_level, log_rotation)

    # Aquire Lock
    lock_file = acquire_lock()
    
    # Read Cache
    cache = read_json(CACHE_FILE)

    # Get Cached IPs
    current_ipv4 = cache.get("ipv4")
    current_ipv6_prefix = cache.get("ipv6_prefix")

    # Get Current IPs
    ipv4_module = config["modules"].get("ipv4")
    if ipv4_module:
        new_ipv4 = execute_script(ipv4_module) or None
        if not new_ipv4:
            logging.warning(f"IPv4 address is {new_ipv4}")

    ipv6_module = config["modules"].get("ipv6")
    if ipv6_module:
        new_ipv6_prefix = execute_script(ipv6_module) or None
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
        logging.info("IP addresses have changed. Updating DynDNS...")
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
