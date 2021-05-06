import time
from conductor.FrinxConductorWrapper import FrinxConductorWrapper
from workers.frinx_rest import conductor_url_base, conductor_headers
import inventory_worker
import lldp_worker
import platform_worker
import vll_worker
import unified_worker
import psql_worker
import vll_service_worker
import vpls_worker
import vpls_service_worker
import bi_service_worker

from workers import common_worker
from workers import import_workflows
from workers import cli_worker
from workers import netconf_worker
from workers import uniconfig_worker
from workers import http_worker
from importDevices import import_devices
import netconf_testtool
import os


workflows_folder_path = '../workflows'
healtchchek_file_path = '../healthcheck'

def main():
    if os.path.exists(healtchchek_file_path):
        os.remove(healtchchek_file_path)


    print('Starting FRINX workers')
    cc = FrinxConductorWrapper(conductor_url_base, 1, 1, headers=conductor_headers)
    cc.start_queue_polling()
    register_workers(cc)
    import_workflows.import_workflows(workflows_folder_path)
    import_devices("../devices/cli_device_data.csv", "../devices/cli_device_import.json")
    import_devices("../devices/netconf_device_data.csv", "../devices/netconf_device_import.json")

    netconf_testtool.write_data_to_netconf_testtool(conductor_url_base, conductor_headers)

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
