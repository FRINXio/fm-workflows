import time
import worker_wrapper
from frinx_rest import conductor_url_base, conductor_headers
import inventory_worker
import lldp_worker
import platform_worker
import vll_worker
import unified_worker
import vll_service_worker
import vpls_worker
import vpls_service_worker
import bi_service_worker
import common_worker
import psql_worker
from import_workflows import import_workflows 
import cli_worker
import netconf_worker
import uniconfig_worker
import http_worker
from importDevices import import_devices 
import os


workflows_folder_path = '../workflows'
healtchchek_file_path = '../healthcheck'

def main():
    if os.path.exists(healtchchek_file_path):
        os.remove(healtchchek_file_path)


    print('Starting FRINX workers')
    cc = worker_wrapper.ExceptionHandlingConductorWrapper(conductor_url_base, 1, 1, headers=conductor_headers)
    register_workers(cc)
    import_workflows(workflows_folder_path)
    import_devices("../devices/cli_device_data.csv", "../devices/cli_device_import.json")
    import_devices("../devices/netconf_device_data.csv", "../devices/netconf_device_import.json")

    with open(healtchchek_file_path, 'w'): pass

    # block
    while 1:
        time.sleep(1000)


def register_workers(cc):
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
