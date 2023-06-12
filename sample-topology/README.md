# Sample topology 

### Requirements

- **HW**
  - Minimum 4gb free ram for simulating all devices
  - Minimum 1gb ram for simulating only CLI devices
- **Running uniconfig**

### Startup
**ST default run only cli devices**

- **Run ./start_sample_topology.sh**
- **Multinode UC** In case of multinode run ./start_sample_topology.sh on manager with arguments and then also need to run ./start_sample_topology.sh on workers without arguments 

#### Optional Parameters

- **-nd | --only-netconf** (Run only netconf devices)

- **-ad | --all** (run all devices)

**Run specific devices (default will run all devices, required atleast 10gb of free RAM)**
-   **-i65 | --iosxr653**   Run only iosxr 653 instance. Devices [iosxr653_1, iosxr653_2]
-   **-i66 | --iosxr663**   Run only iosxr 663 instance. Devices [iosxr663_1]
-   **-j | --junos**        Run only junos instance. Devices [junos_1]


### Developers

#### Build docker image - frinx/sample-topology:<TAG>
To build docker image run script `./build_st_docker_image.sh frinx/sample-topology:<TAG>`
