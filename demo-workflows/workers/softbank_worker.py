from frinx_conductor_workers import uniconfig_worker
import util


def create_vrf(node_id,vrf_name, locator_prefix):
    url = f"/openconfig-network-instance:network-instances/network-instance={vrf_name}"
    vrf_config = {"network-instance":[{
          "name": vrf_name,
          "config": {
            "name": vrf_name
          },
          "protocols": {
            "protocol": [
              {
                "identifier": "openconfig-policy-types:BGP",
                "name": "default",
                "bgp": {
                  "global": {
                    "arcos-openconfig-bgp-augments:srv6": {
                      "config": {
                        "locator": locator_prefix
                      }
                    }
                  }
                },
                "config": {
                  "name": "default",
                  "identifier": "openconfig-policy-types:BGP"
                }
              }
            ]
          }
        }]}

    vrf_response = uniconfig_worker.write_structured_data({'inputData': {
        'device_id': node_id,
        'uri': url,
        "template": vrf_config,
        'params': {},
        "method": "PUT"
    }})
    return vrf_response


def srv6_configure_device(task):
    node_id = task["inputData"]["node_id"]
    ipv6 = task["inputData"]["ipv6"]
    ipv6_prefix = task["inputData"]["ipv6_prefix"]
    vrf_name = task["inputData"]["vrf_name"]

    locator_prefix = f"{task['inputData']['vrf_name']}_locator_prefix"

    url = "/openconfig-network-instance:network-instances/network-instance=default/arcos-srv6:srv6"

    locator_config = { "arcos-srv6:srv6": {
            "locator": [
              {
                "name": locator_prefix,
                "config": {
                  "prefix": f"{ipv6}/{ipv6_prefix}"
                }
              }
            ]
          }}

    locator_response = uniconfig_worker.write_structured_data({'inputData': {
        'device_id': node_id,
        'uri': url,
        "template": locator_config,
        'params': {},
        "method": "PATCH"
    }})

    vlan_response = uniconfig_worker.read_structured_data({'inputData': {
        'device_id': node_id,
        'uri': f"/openconfig-network-instance:network-instances/network-instance={vrf_name}",
    }})

    if vlan_response["output"]["response_code"] != 200:
        vrf_response = create_vrf(node_id, vrf_name, locator_prefix)
    else:
        url_vrf = f"/openconfig-network-instance:network-instances/network-instance={vrf_name}/protocols/protocol=openconfig-policy-types%3ABGP,default"
        vrf_config ={
                "protocol": [
                    {
                        "identifier": "openconfig-policy-types:BGP",
                        "name": "default",
                        "bgp": {
                            "global": {
                                "arcos-openconfig-bgp-augments:srv6": {
                                    "config": {
                                        "locator": locator_prefix
                                    }
                                }
                            }
                        },
                        "config": {
                            "name": "default",
                            "identifier": "openconfig-policy-types:BGP"
                        }
                    }
                ]
            }

        vrf_response = uniconfig_worker.write_structured_data({'inputData': {
            'device_id': node_id,
            'uri': url_vrf,
            "template": vrf_config,
            'params': {},
            "method": "PUT"
        }})

    return util.completed_response({"vrf_response": vrf_response, "locator_response": locator_response})


def start(cc):

  cc.register(
        "SRv6_configure_device",
        {
            "description": '{"description": "Configure SRv6 to device configuration"}',
            "inputKeys": [
                "node_id",
                "ipv6",
                "ipv6_prefix",
                "vrf_name"
            ],
            "outputKeys": ["response_body"],
        },
        srv6_configure_device,
    )