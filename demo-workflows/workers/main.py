import os
import json
import logging.config
import requests
from pathlib import Path

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from conductor.FrinxConductorWrapper import FrinxConductorWrapper
from frinx_conductor_workers.frinx_rest import conductor_url_base, conductor_headers


from importDevices import import_devices

# Suppress InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

log = logging.getLogger(__name__)

WORKFLOWS_DIR: Path = Path("../workflows")
HEALTCHCHEK_FILE: Path = Path("../healthcheck")


def configure_logging(
        default_path='logging-config.json', default_level=logging.INFO, env_key='LOG_CFG'
) -> None:
    """Setup logging configuration"""

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


def _import_devices() -> None:

    import_devices("../devices/cli_device_data.csv", "../devices/cli_device_import.json")
    # Sample topology 2 import devices
    import_devices("../devices/cli_saos_device_data.csv",
                   "../devices/cli_saos_device_import.json")
    import_devices("../devices/netconf_device_data_iosxr.csv",
                   "../devices/netconf_device_import_iosxr.json")
    import_devices("../devices/netconf_device_data.csv",
                   "../devices/netconf_device_import.json")


def _register_workers(conductor) -> None:

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
    import device_worker
    import lldp_identification_worker
    # import vll_worker
    # import vll_service_worker
    # import vpls_worker
    # import vpls_service_worker
    # import bi_service_worker

    cli_worker.start(conductor)
    netconf_worker.start(conductor)
    uniconfig_worker.start(conductor)
    common_worker.start(conductor)
    http_worker.start(conductor)
    platform_worker.start(conductor)
    lldp_worker.start(conductor)
    inventory_worker.start(conductor)
    unified_worker.start(conductor)
    psql_worker.start(conductor)
    device_worker.start(conductor)
    lldp_identification_worker.start(conductor)

    # vll_worker.start(cc)
    # vll_service_worker.start(cc)
    # vpls_worker.start(cc)
    # vpls_service_worker.start(cc)
    # bi_service_worker.start(cc)


def _import_workflows(workflows_dir: Path = WORKFLOWS_DIR) -> None:
    from frinx_conductor_workers import import_workflows

    import_workflows.import_workflows(workflows_dir)


def _configure_healthcheck(file: Path = HEALTCHCHEK_FILE) -> None:
    """
    Creates a file at a specified path, it's later checked for existence.

    This isn't a good solution and should be improved.

    Args:
        file: an absolute or a relative path to a file
    """
    if file.exists():
        os.remove(file)

    with file.open(mode="w"):
        pass


def main():
    configure_logging()
    logger = logging.getLogger(__name__)

    conductor = FrinxConductorWrapper(
        server_url=conductor_url_base,
        headers=conductor_headers,
        polling_interval=1,
        max_thread_count=200
    )

    _register_workers(conductor)
    logger.info("All workers are registered")

    _import_workflows()
    logger.info("All workflows are imported")

    _import_devices()
    logger.info("All devices are imported")

    _configure_healthcheck()
    logger.debug("Health check is configured")

    logger.debug("Starting workers's threads (this blocks the main thread)")
    conductor.start_workers()


if __name__ == '__main__':
    main()
