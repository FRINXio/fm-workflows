# fm-workflows

## For users
Download container images with
```
./install.sh
```

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
In the cypress folder there are GUI tests.

### Install Cypress
See [Cypress][cypress]

Install optionally prerequisites for cypress (only if you experience problems with during cypress run):
```
sudo apt-get -y install libgtk-3-0 libnotify-dev libgconf-2-4 libxss1 xvfb

VERSION=v12.16.1
DISTRO=linux-x64
wget https://nodejs.org/dist/$VERSION/node-$VERSION-$DISTRO.tar.xz
sudo mkdir -p /usr/local/lib/nodejs
sudo tar -xJvf node-$VERSION-$DISTRO.tar.xz -C /usr/local/lib/nodejs
export PATH=/usr/local/lib/nodejs/node-$VERSION-$DISTRO/bin:$PATH
```
Install cypress:
```
cd cypress-test
```
```
npm install cypress
```
Install cypress plugin:
```
npm install @4tw/cypress-drag-drop
```

### Install Chrome
```
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get -y install google-chrome-stable
```

### Execute tests
Cypress expects default localization of tests in folder ```./cypress/integration```.
The file ./cypress.json defines the defaults - it is expected that FRINX-machine is run locally.
Then you can run tests interactivelly by issuing the command:
```
cd cypress-test
```
```
node_modules/.bin/cypress open --browser chrome
```
Note: use 'cypress open' for interactive testing

In case you need to test remote FRINX-machine instance
you can run tests after providing of proper IP and credentials from command line like this:
```
CYPRESS_baseUrl=http://10.103.5.231 \
CYPRESS_viewportHeight=900 \
CYPRESS_viewportWidth=1440 \
CYPRESS_inventory=http://10.103.5.231:5601 \
CYPRESS_login=example@example.com \
CYPRESS_password=your_password \
CYPRESS_SKIP_LOGIN=false \
~/node_modules/.bin/cypress run --browser chrome --headless
```
Note: use 'cypress run' for automatic testing

[cypress]: https://docs.cypress.io/guides/getting-started/installing-cypress.html
