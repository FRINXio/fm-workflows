//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices teardown', function() {
  it('goes to inventory and deletes BIG_ONE_ROUTER', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/elasticsearch/_msearch?rest_total_hits_as_int=true&ignore_throttled=true').as('getSearchResults')

    //After the workflow has completed, go to Kibana and look for an entry called “lldp”.
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')

    cy.contains('Discover',{timeout:20000}).click()
    //cy.get('div.ui-select-match > span > i.caret.pull-right').click({force:true})
    cy.get('i.caret.pull-right').click({force:true})
    cy.contains('inventory-device').click({force:true})
    cy.wait('@getSearchResults')
    //explicit wait
    cy.wait(500)
    cy.get('td').click({force:true,multiple:true})

    cy.get("dd span").contains('BIG_ONE_ROUTER').scrollIntoView()

    cy.contains('Dev Tools',{timeout:10000}).click()
    cy.get('button[i18n-id="console.welcomePage.closeButtonLabel"]',{timeout:10000}).contains('Get to work',{timeout:10000}).click({force:true})

    // DELETE inventory-device/device/BIG_ONE_ROUTER
    cy.get('div.kbnUiAceKeyboardHint').next().invoke('show').type('{selectall}{del} DELETE inventory-device/device/BIG_ONE_ROUTER{ctrl}{enter}',{force:true})
    cy.wait(1000)
  })

  it('goes to inventory and deletes GREATER_ONE_ROUTER', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/elasticsearch/_msearch?rest_total_hits_as_int=true&ignore_throttled=true').as('getSearchResults')

    //After the workflow has completed, go to Kibana and look for an entry called “lldp”.
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')

    cy.contains('Discover',{timeout:20000}).click()
    //cy.get('div.ui-select-match > span > i.caret.pull-right').click({force:true})
    cy.get('i.caret.pull-right').click({force:true})
    cy.contains('inventory-device').click({force:true})
    cy.wait('@getSearchResults')
    //explicit wait
    cy.wait(500)
    cy.get('td').click({force:true,multiple:true})

    cy.get("dd span").contains('GREATER_ONE_ROUTER').scrollIntoView()

    cy.contains('Dev Tools',{timeout:10000}).click()
    cy.get('button[i18n-id="console.welcomePage.closeButtonLabel"]',{timeout:10000}).contains('Get to work',{timeout:10000}).click({force:true})

    // DELETE inventory-device/device/GREATER_ONE_ROUTER
    cy.get('div.kbnUiAceKeyboardHint').next().invoke('show').type('{selectall}{del} DELETE inventory-device/device/GREATER_ONE_ROUTER{ctrl}{enter}',{force:true})
    cy.wait(1000)
  })
})
