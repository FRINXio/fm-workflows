# fm-workflows

## For users
Make sure FRINX-machine (https://github.com/FRINXio/FRINX-machine) is running. <br>
<br>To attach containers to running FM swarm deployment
```
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

[cypress]: https://docs.cypress.io/guides/getting-started/installing-cypress.html
