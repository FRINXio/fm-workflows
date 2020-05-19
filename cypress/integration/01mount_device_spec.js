describe('Mount devices from UniConfig', function() {
  beforeEach(function() {
    cy.login()
  })

  //OPTIONAL: this test is run immediatelly after starting of frinx machine
  //OPTIONAL: no device is mounted
  it('Mount a cli device', function() {
    var device_id='XR01'

    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfig')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfigO')

    cy.visit('/')
    cy.contains('UniConfig').click()

    cy.url().should('include', '/devices')

    //cy.get('table tbody tr').should('not.to.exist')
    cy.contains('Mount Device').click()

    cy.contains('CLI').click()
    cy.contains('Basic').click()

    cy.get('#mountcliInput-node-id')
      .clear()
      .type(device_id)
      .should('have.value', device_id)

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

    cy.contains('Advanced').click()
    cy.contains('Basic').click()

    cy.get('button[class="btn btn-primary"]').contains('Mount Device').click()

    cy.get('button[class="btn btn-primary"]').should('not.to.exist')
    cy.get('button.btn.btn-success', { timeout : 30000  } ).should('contain','Connected')
    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')

    //cy.get('table tbody tr').should('have.length',1)
    cy.get('table tbody tr').should('to.exist')
    cy.contains(device_id).click()

    cy.get('div.modal-dialog.modal-lg')
    cy.contains('Basic').click()
    cy.get('input[value="connected"]')
    cy.contains('Available capabilities').click()
    cy.contains('Unavailable capabilities').click()
    cy.contains('Commit error patterns').click()
    cy.contains('Error patterns').click()

    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')
    //20200518THIS WORKED IN V1.1 BUT STOPPED TO WORK IN V1.2 DUE TO CHANGE OF CLASS (ALIGN CENTER-> ALIGN LEFT)
    cy.contains(device_id).parent().find('td').eq(0).find('div input').click()
    cy.contains(device_id).parent().find('td').eq(0).find('div input').click()
    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    //20200518 wait only for the second xhr
    cy.wait('@getConfigO')
    cy.url().should('include', '/devices/edit/' + device_id)
    cy.get('button[class~="round"]').click({force:true})
    cy.contains('Refresh').click()

    //cy.contains(device_id).parent().find('td').eq(0).find('div input').click()
    //cy.contains('Unmount Devices').click()
    //cy.get('table tbody tr').should('not.to.exist')
  })

  it('Mount a netconf device', function() {
    var device_id='netconf-testtool'

    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfig')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfigO')

    cy.visit('/')
    cy.contains('UniConfig').click()
    cy.url().should('include', '/devices')

    cy.contains('Mount Device').click()

    cy.contains('Netconf').click()
    cy.get('#mountTabs-tabpane-Netconf').contains('Basic').click()

    cy.get('#mountnetconfInput-node-id')
      .clear()
      .type(device_id)
      .should('have.value', device_id)

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

    cy.get('#mountTabs-tabpane-Netconf').contains('Advanced').click()
    cy.contains('UniConfig Native').click()
    cy.contains('Blacklist').parent().find(':checkbox').click()

    cy.get('#mountTabs-tabpane-Netconf').contains('Basic').click()

    cy.get('button[class="btn btn-primary"]').contains('Mount Device').click()

    cy.get('button[class="btn btn-primary"]').should('not.to.exist')
    cy.get('button.btn.btn-success', { timeout : 30000  } ).should('contain','Connected')
    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')

    //cy.get('table tbody tr').should('have.length',2)
    cy.get('table tbody tr').should('to.exist')
    cy.contains(device_id).click()

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
    //20200518THIS WORKED IN V1.1 BUT STOPPED TO WORK IN V1.2 DUE TO CHANGE OF CLASS (ALIGN CENTER-> ALIGN LEFT)
    cy.contains(device_id).parent().find('td').eq(0).find('div input').click()
    cy.contains(device_id).parent().find('td').eq(0).find('div input').click()
    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    //20200518 wait only for the second xhr
    cy.wait('@getConfigO')
    cy.url().should('include', '/devices/edit/' + device_id)

    cy.get('button[class~="round"]').click({force:true})
    cy.contains('Refresh').click()

    //cy.contains(device_id).parent().find('td').eq(0).click()
    //cy.contains('Unmount Devices').click()
    //cy.get('table tbody tr').should('not.to.exist')
  })
})

