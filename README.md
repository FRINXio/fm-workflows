# fm-workflows

## Usage
Make sure FRINX-machine is running, navigate to `cd /fm-workflows` and execute `./startup.sh`. Imported workflows and tasks will appear in FRINX-Machine UI, right after importing finishes.

## Cypress e2e tests
In the cypress folder there are GUI tests

### Install Cypress
See [Cypress][cypress]
```
npm install cypress
```

### Install Chrome
```
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add 
echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update 
sudo apt-get -y install google-chrome-stable
```

### Execute tests
Cypress expects default localization of tests in folder ```~/cypress/integration```
You can run tests after providing of proper IP and credentials from command line like this:
``` 
CYPRESS_baseUrl=http://10.103.5.231 \
CYPRESS_inventory=http://10.103.5.231:5601 \
CYPRESS_login=example@example.com \
CYPRESS_password=your_password \
~/node_modules/.bin/cypress run --browser chrome --headless
```

[cypress]: https://docs.cypress.io/guides/getting-started/installing-cypress.html
