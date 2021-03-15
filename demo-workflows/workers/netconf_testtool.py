import requests
import time
import socket


def port_check(host, port):
    soc_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_con.settimeout(10)
    try:
        soc_con.connect((host, port))
        print("Open Port Check: " + str(host) + ": " + str(port) + "is open")
        return True
    except:
        print("Open Port Check: " + str(host) + ": " + str(port) + "is unavailable")
        time.sleep(1)
        return False


def write_data_to_netconf_testtool(wp_url, wp_headers):

    payload = {"name": "Write_data_to_netconf_testool", "version": 1, "input": {}}
    st_port_visible = False
    workflow_id = False

    while st_port_visible is not True:
        st_port_visible = port_check('sample-topology', 1783)

    status = ''

    for x in range(5):
        response = requests.post(wp_url + "/workflow", json=payload, headers=wp_headers)
        print("Write_data_to_netconf_testool: " + str(response.text) + ", response: " + str(response.status_code))

        if response.status_code == 200 and len(str(response.text)) < 40:
            workflow_id = True
        else:
            time.sleep(20)

        if workflow_id is True:
            for y in range(5):
                r = requests.get(wp_url.replace("proxy/api", "id/" + response.text), headers=wp_headers)
                if r.status_code == 200:
                    data = r.json()
                    status = data['result']['status']
                    if status == "COMPLETED" or status == "FAILED":
                        break
                    else:
                        time.sleep(10)
                else:
                    time.sleep(10)
                    print("Write_data_to_netconf_testool: " + str(r.status_code))

        if status is not '':
            print("Write_data_to_netconf_testool: " + str(status))
            break
