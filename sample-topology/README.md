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

- **--only-netconf** (Run only netconf devices)

- **--all** (run all devices)


### Developers

#### Build docker image - frinx/sample-topology:<TAG>
To build docker image run script `./build_st_docker_image.sh frinx/sample-topology:<TAG>`
