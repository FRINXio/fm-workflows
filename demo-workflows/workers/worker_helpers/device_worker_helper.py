import re

NETCONF_MOUNT_BODY = {"keepalive-delay": "10", "tcp-only": "false", "reconcile": "false",
                      "sleep-factor": "1", "between-attempts-timeout-millis": "10000",
                      "connection-timeout-millis": "30000","dry-run-journal-size": "150" ,"uniconfig-native": "true",
                      "max-connection-attempts": "1", "default-request-timeout-millis": "60000",
                      "uniconfig-native-enabled": "true", "edit-config-test-option": "set",
                      "enabled-notifications": False
                      }

NETCONF_URI_DICT = {
    "cisco-ios-xr-653": {
        "uri": {
            "version": "/Cisco-IOS-XR-plat-chas-invmgr-oper:platform-inventory/racks/rack=0/attributes/basic-info/software-revision",
            "model": "/Cisco-IOS-XR-plat-chas-invmgr-oper:platform-inventory/racks/rack=0/attributes/basic-info/model-name",
            "hostname": "/Cisco-IOS-XR-shellutil-cfg:host-names/host-name",
        },
        "details": {"vendor": "cisco", "sw": "ios xr"},
    },
    "cisco-ios-xr-663": {
            "uri": {
                "version": "/Cisco-IOS-XR-plat-chas-invmgr-ng-oper:platform-inventory/racks/rack=0/attributes/basic-info/software-revision",
                "model": "/Cisco-IOS-XR-plat-chas-invmgr-ng-oper:platform-inventory/racks/rack=0/attributes/basic-info/model-name",
                "hostname": "/Cisco-IOS-XR-shellutil-cfg:host-names/host-name",
            },
            "details": {"vendor": "cisco", "sw": "ios xr"},
        },
    "juniper": {
        "uri": {
            "version": "/configuration/version?content=config",
            "hostname": "/configuration/system/host-name?content=config"},
        "details": {"vendor": "juniper", "sw": "junos"},
    },
    "nokia": {
        "uri": {
            "version": "/nokia-state:state/system/version/version-number?content=nonconfig",
            "model": "/nokia-state:state/system/platform?content=nonconfig",
            "hostname": "/nokia-state:state/system/oper-name?content=nonconfig"},
        "details": {"vendor": "nokia", "sw": "sros"},
    },
}

SCHEMA_BLACKLIST = {"cisco-ios-xr": [
    "openconfig-interfaces:interfaces",
    "openconfig-lacp:lacp",
    "ietf-interfaces:interfaces",
    "openconfig-vlan:vlans",
    "openconfig-routing-policy:routing-policy",
    "openconfig-lldp:lldp",
    "Cisco-IOS-XR-group-cfg:groups",
    "openconfig-acl:acl",
    "openconfig-network-instance:network-instances"
]}


def get_device_model(line: str, actual_value: str) -> str:
    """ Apply regexes to line if any is successfully return value else return actual value"""
    cisco_model_number_re = re.search(r"^Model number\s+:\s*(\S+)", str(line))
    cisco_model_software_re = re.search(r", (\S+) Software", str(line))
    cisco_model_series_re = re.search(r"cisco (\S+) Series", str(line))
    cisco_model_processor = re.search(r"cisco (\S+) \(\) processor", str(line))
    ciena_model_re = re.search(r"(\d{4})\S* Configuration File", str(line))
    junos_model_re = re.search(r"Model:\s*(\S+)", str(line))
    regex_list = [cisco_model_number_re, cisco_model_software_re, cisco_model_series_re, cisco_model_processor,
                  ciena_model_re, junos_model_re]

    for regex in regex_list:
        if regex:
            return regex.group(1)
    return actual_value
