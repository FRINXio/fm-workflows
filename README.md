# fm-workflows

## For users
Download container images with
```sh
./install.sh
```

Make sure FRINX-machine (https://github.com/FRINXio/FRINX-machine) is running. <br>
<br>To attach containers to running FM swarm deployment (please check allowed parameters in below section sample topology)
```sh
./startup.sh
```

<br>Check status of services.
Each service has REPLICAS 1/1 when everything works (it may take several minutes to start all services).
```
docker service ls
```

<br>To stop and remove all services
```
docker stack rm fm
```

<br>To remove old data if needed
```
docker volume prune
```

<br>To remove single service from deployment
```
docker service rm <swarm-service-name>
```

## For developers
### Building images
Sample-topology project contains a submodule which needs to initalized first.
```
git submodule update --init --recursive
```

<br>To build a custom docker images for a service:
```
docker build -f sample-topology/Dockerfile -t frinx/fm-sample-topology:latest ./sample-topology/
docker build -f demo-workflows/Dockerfile -t frinx/demo-workflows:latest ./demo-workflows/
```


## Cypress e2e tests
In the cypress-test folder are the GUI tests.

### Execute tests
Cypress expects default localization of tests in folder ```.cypress-tests/cypress/integration```.
The file ./cypress.json defines the defaults - it is expected that FRINX-machine is run locally.
Then you can run tests by:
```
cd cypress-test
```
Interactively:
Set xhost access control list:
```
xhost local:root
```
Run cypress:
```
docker run -it \
  -v $PWD:/e2e \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -w /e2e \
  -e DISPLAY \
  --entrypoint cypress \
  --network=frinx-machine \
  cypress/included:6.2.0 open --project .
```
Automatically:
```
 docker run -it  --network=frinx-machine -v $PWD:/e2e -w /e2e cypress/included:6.2.0
```

# Sample topology
### Requirements

- **HW**
  - Minimum 6gb free ram for simulating all devices
  - Minimum 1gb ram for simulating only CLI devices
- **Running uniconfig**

### Startup
**ST default run only cli devices**

- **Run ./startup.sh**
- **Multinode UC** In case of multinode run ./startup.sh on manager with arguments and then also need to run ./startup.sh on workers without arguments 

#### Optional Parameters

- **-nd | --only-netconf-devices** (Run only netconf devices)
- **-ad | --all-devices** (Run all devices CLI + Netconf. There can be added filtering netconf instances ex. --iosxr653 will run all CLI devices and iosxr653 netconf device)
- **-ci | --clean-inventory** ( Clean device inventory. Devices will not be uninstalled from UC !)


**Run specific netconf devices**:

Each netconf testtool instance need atleast 2gb free ram if you dont have enough free ram you can run only selected netconf instances.
-   **-i65 | --iosxr653**   Run only iosxr 653 instance. Devices [iosxr653_1, iosxr653_2]
-   **-i66 | --iosxr663**   Run only iosxr 663 instance. Devices [iosxr663_1]
-   **-j | --junos**        Run only junos instance. Devices [junos_1]

**Parameter examples:**

``./startup.sh`` - Run all CLI devices

``./startup.sh -ci -nd`` - Clean device inventory and then run all netconf devices 

``./startup.sh -ci -nd -i65`` - Clean device inventory and run only iosxr653_1 and iosxr653_2 devices

``./startup.sh -ci -ad -j -i66`` - Clean device inventory, run all cli devices and run also junos_1 and iosxr663 netconf devices

**List of simulated devices**

```
<NAME> <LOCALHOST_PORT>
------- CLI -------
saos6_1 10000
saos6_2 10001
saos8_1 10002
saos8_2 10003
cisco_IOS_1 10004
cisco_IOS_2 10005
cisco_XR_1 10006
cisco_XR_2 10007
huawei_VRP 10008
leaf1 10009
leaf2 10010
leaf3 10011
leaf4 10012
leaf5 10013
spine1 10014
spine2 10015

------- NETCONF -------
iosxr653_1 17000
iosxr653_2 17001
iosxr663_1 17100
junos_1 17200
```




[cypress]: https://docs.cypress.io/guides/getting-started/installing-cypress.html
