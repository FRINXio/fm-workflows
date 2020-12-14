//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices', function() {
  it.skip('prepares index', function() {
    cy.server()
    cy.route('**?pattern=inventory-device&**').as('getXhr')
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    //this is needed only for the first time
    //cy.contains('Explore on my own',{timeout:10000}).click()
    cy.contains('Management',{timeout:20000}).click()
    cy.contains('Index Patterns',{timeout:10000}).click({force:true})
    cy.get('button[data-test-subj="createIndexPatternButton"]').click({force:true})
    cy.get('input[name="indexPattern"][data-test-subj="createIndexPatternNameInput"]').clear({force:true}).type('inventory-device{del}',{force:true})
    cy.contains('Success! Your index pattern matches 1 index.')
    cy.contains('Next step',{timeout:10000}).click({force:true})
    cy.wait('@getXhr')
    cy.get('button[data-test-subj="createIndexPatternCreateButton"]').contains('Create index pattern',{timeout:10000}).click({force:true})
    cy.contains('Creating index pattern…')
    cy.contains('inventory-device')
  })

  it('retrieves data', function() {
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
    cy.get("dd span").contains('GREATER_ONE_ROUTER').scrollIntoView()

    //cy.contains('Dev Tools',{timeout:10000}).click()
    //cy.get('button[i18n-id="console.welcomePage.closeButtonLabel"]',{timeout:10000}).contains('Get to work',{timeout:10000}).click({force:true})

    // DELETE inventory-device/device/GREATER_ONE_ROUTER
    // DELETE inventory-device/device/BIG_ONE_ROUTER
    //cy.get('div.kbnUiAceKeyboardHint').next().invoke('show').type('{selectall}{del} DELETE inventory-device/device/BIG_ONE_ROUTER{ctrl}{enter}',{force:true})
    //cy.get('div.kbnUiAceKeyboardHint').next().invoke('show').type('{selectall}{del} DELETE inventory-device/device/GREATER_ONE_ROUTER{ctrl}{enter}',{force:true})
  })
})
