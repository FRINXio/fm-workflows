describe('Mount devices from UniConfig', function() {
  beforeEach(function() {
    cy.login()
  })

  //this test is run immediatelly after starting of frinx machine
  //no device is mounted
  it('Mount cli device with toggle bug workaround', function() {
    cy.visit('/')
    cy.contains('UniConfig').click()

    cy.url().should('include', '/devices')

    cy.get('table tbody tr').should('not.to.exist')
    cy.contains('Mount Device').click()

    cy.contains('CLI').click()
    cy.contains('Basic').click()

    cy.get('#mountcliInput-node-id')
      .clear()
      .type('XR01')
      .should('have.value', 'XR01')

    cy.get('#mountcliInput-host')
      .clear()
      .type('sample-topology')
      .should('have.value', 'sample-topology')

    cy.get('#mountcliInput-port')
      .clear()
      .type('10001')
      .should('have.value', '10001')

    cy.get('label[for="mountcliInput-transport-type"] ~ div[class="Dropdown-root"] > div[class="Dropdown-control"] > div[class="Dropdown-arrow-wrapper"] > span')
      .click()
    cy.get('div[class^="Dropdown-option"]').contains('ssh')
      .click()

    //second click to toggle back to ssh
    //BUG workaround
    //TODO temove this later
    cy.get('label[for="mountcliInput-transport-type"] ~ div[class="Dropdown-root"] > div[class="Dropdown-control"] > div[class="Dropdown-arrow-wrapper"] > span')
      .click()
    cy.get('div[class^="Dropdown-option"]').contains('ssh')
      .click()


    cy.get('label[for="mountcliInput-transport-type"] ~ div[class="Dropdown-root"] > div[class="Dropdown-control"] > div[class="Dropdown-placeholder is-selected"]')
      .contains('ssh')

    cy.get('label[for="mountcliInput-device-type"] ~ div[class="Dropdown-root"] > div[class="Dropdown-control"] > div[class="Dropdown-arrow-wrapper"] > span')
      .click()
    cy.get('div[class^="Dropdown-option"]').contains('ios xr')
      .click()

    cy.get('label[for="mountcliInput-device-version"] ~ div[class="Dropdown-root"] > div[class="Dropdown-control"] > div[class="Dropdown-arrow-wrapper"] > span')
      .click()
    cy.get('div[class^="Dropdown-option"]').contains('6.*')
      .click()

    cy.get('#mountcliInput-username')
      .clear()
      .type('cisco')
      .should('have.value', 'cisco')

    cy.get('#mountcliInput-password')
      .clear()
      .type('cisco')
      .should('have.value', 'cisco')

    cy.get('button[class="btn btn-primary"]').contains('Mount Device')
      .then(($button) => {
      $button.click()
      })

    cy.get('button[class="btn btn-primary"]').should('not.to.exist')
    cy.get('button.btn.btn-success', { timeout : 10000  } ).should('contain','Connected')
    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')

    //cy.get('table tbody tr').should('have.length',1)
    cy.get('table tbody tr').should('to.exist')
    cy.contains('XR01').click()

    cy.get('div.modal-dialog.modal-lg')
    cy.contains('Basic').click()
    cy.get('input[value="connected"]')
    cy.contains('Available capabilities').click()
    cy.contains('Unavailable capabilities').click()
    cy.contains('Commit error patterns').click()
    cy.contains('Error patterns').click()

    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')
    cy.contains('XR01').parent().find('td').eq(0).click()
    cy.contains('XR01').parent().find('td').eq(0).click()
    cy.contains('XR01').parent().find('td').eq(5).click()
    cy.url().should('include', '/devices/edit/XR01')
    cy.get('button[class~="round"]').click({force:true})
    cy.contains('Refresh').click()

    //cy.contains('XR01').parent().find('td').eq(0).click()
    //cy.contains('Unmount Devices').click()
    //cy.get('table tbody tr').should('not.to.exist')
  })

  it('Mount netconf device', function() {
    cy.visit('/')
    cy.contains('UniConfig').click()
    cy.url().should('include', '/devices')

    cy.get('table tbody tr').should('not.to.exist')
    cy.contains('Mount Device').click()

    cy.contains('Netconf').click()
    // this does not work - why ??? cy.contains('Basic').click()
    //cy.get('div.tab-content').contains('Basic', {force:true}).click()// nefunguje lebo najde prvy Basic na prvom paneli ktory je hidden
    cy.get('#mountTabs-tabpane-Netconf').contains('Basic').click()

    cy.get('#mountnetconfInput-node-id')
      .clear()
      .type('netconf-testtool')
      .should('have.value', 'netconf-testtool')

    cy.get('#mountnetconfInput-host')
      .clear()
      .type('sample-topology')
      .should('have.value', 'sample-topology')

    cy.get('#mountnetconfInput-port')
      .clear()
      .type('1783')
      .should('have.value', '1783')

    cy.get('#mountnetconfInput-username')
      .clear()
      .type('cisco')
      .should('have.value', 'cisco')

    cy.get('#mountnetconfInput-password')
      .clear()
      .type('cisco')
      .should('have.value', 'cisco')

    cy.get('#mountTabs-tabpane-Netconf').contains('Advanced').click()
    cy.contains('UniConfig Native').click()
    cy.contains('Blacklist').parent().find(':checkbox').click()




    cy.get('button[class="btn btn-primary"]').contains('Mount Device')
      .then(($button) => {
      $button.click()
      })

    cy.get('button[class="btn btn-primary"]').should('not.to.exist')
    cy.get('button.btn.btn-success', { timeout : 10000  } ).should('contain','Connected')
    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')

    //cy.get('table tbody tr').should('have.length',2)
    cy.get('table tbody tr').should('to.exist')
    cy.contains('netconf-testtool').click()

    cy.get('div.modal-dialog.modal-lg')
    cy.contains('Basic').click()
    cy.get('input[value="connected"]')
    cy.contains('Available capabilities').click()
    cy.contains('Unavailable capabilities').click()
    //cy.contains('Commit error patterns').click()
    //cy.contains('Error patterns').click()
    cy.contains('Basic').click()

    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')
    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('netconf-testtool').parent().find('td').eq(5).click()
    cy.url().should('include', '/devices/edit/netconf-testtool')
    cy.get('button[class~="round"]').click({force:true})
    cy.contains('Refresh').click()

    //cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    //cy.contains('Unmount Devices').click()
    //cy.get('table tbody tr').should('not.to.exist')
  })
})

