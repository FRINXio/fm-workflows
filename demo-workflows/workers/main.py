import os
import time
import json
import logging.config
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from conductor.FrinxConductorWrapper import FrinxConductorWrapper
from frinx_conductor_workers.frinx_rest import conductor_url_base, conductor_headers
from frinx_conductor_workers import import_workflows

from frinx_conductor_workers import common_worker
from frinx_conductor_workers import cli_worker
from frinx_conductor_workers import netconf_worker
from frinx_conductor_workers import uniconfig_worker
from frinx_conductor_workers import http_worker

import inventory_worker
import lldp_worker
import platform_worker
import unified_worker
import psql_worker
import vll_worker
import vll_service_worker
import vpls_worker
import vpls_service_worker
import bi_service_worker

from importDevices import import_devices

# Suppress InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

log = logging.getLogger(__name__)

workflows_folder_path = '../workflows'
healtchchek_file_path = '../healthcheck'

def setup_logging(
        default_path='logging-config.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration
    """
    path = os.path.join(os.path.dirname(__file__), default_path)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def main():
    setup_logging()

    if os.path.exists(healtchchek_file_path):
        os.remove(healtchchek_file_path)

    log.info('Starting FRINX workers')
    cc = FrinxConductorWrapper(conductor_url_base, 1, 1, headers=conductor_headers)
    register_workers(cc)
    import_workflows.import_workflows(workflows_folder_path)

    import_devices("../devices/cli_device_data.csv", "../devices/cli_device_import.json")
    import_devices("../devices/netconf_device_data.csv", "../devices/netconf_device_import.json")

    cc.start_workers()

    with open(healtchchek_file_path, 'w'): pass

    # block
    while 1:
        time.sleep(1000)


def register_workers(cc):
    cli_worker.start(cc)
    netconf_worker.start(cc)
    uniconfig_worker.start(cc)
    common_worker.start(cc)
    http_worker.start(cc)
    platform_worker.start(cc)
    lldp_worker.start(cc)
    inventory_worker.start(cc)
    unified_worker.start(cc)
    psql_worker.start(cc)
    # vll_worker.start(cc)
    # vll_service_worker.start(cc)
    # vpls_worker.start(cc)
    # vpls_service_worker.start(cc)
    # bi_service_worker.start(cc)


if __name__ == '__main__':
    main()