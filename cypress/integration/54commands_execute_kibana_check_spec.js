//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html#execute-saved-command-on-mounted-devices
//Execute saved command on mounted devicesa - workflow Execute_and_read_rpc_cli_device_from_inventory_update_inventory
//put to inventory new field named after command_id and its value should be output of the command
describe('Check that executed command is stored in the inventory', function() {
  it.skip('prepares index inventory-device', function() {
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
    //this is there only for the first time cy.route('/api/index_patterns/_fields_for_wildcard?pattern=inventory-device&meta_fields=[').as('getInventoryDeviceData')
	  
    //After the workflow has completed, go to Kibana and look for an entry called “inventory-device”. 
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    cy.contains('Discover',{timeout:20000}).click()
	  
    //cy.get('div.ui-select-match > span > i.caret.pull-right').click({force:true})
    cy.get('i.caret.pull-right').click({force:true})
    //cy.contains('inventory-device*').click({force:true})
    cy.contains('inventory-device').click({force:true})
    cy.wait('@getSearchResults')
    //explicit wait
    //cy.wait(1000)
    //this would work maybe for the first time - but will time out later - why? some caching for the first time ?- cy.wait('@getInventoryDeviceData')
    //let us try instead of explicite wait this
    cy.get('table tbody tr:nth-child(8)').should('to.exist')
	  
    //cy.get('button.kbnDocTableOpen__button').click({multiple:true})
    //cy.get('td[ng-click="toggleRow()"]').click({multiple:true})
    cy.get('td[data-test-subj="docTableExpandToggleColumn"]').click({force:true,multiple:true})
    //cy.get('div.row').scrollTo('bottom', { easing: 'linear',force:true })
    //cy.scrollTo('top', { easing: 'linear' })
    //cy.get('input[type="search"]').type('inventory-device*',{force:true})
    //cy.get('div.kbnGlobalNavLink__title').click()
    //cy.get('div.iframes-container').click()
    //  doc.find('div.kbnGlobalNav__links > div > app-switcher > div.kbnGlobalNavLink > a').click(() => {
    cy.get("dd span").contains('IOS01').scrollIntoView()
    cy.get('td[field-name="field"]').contains('sh_run').scrollIntoView()
    cy.get('td[field-name="field"]').contains('sh_run').parent().next().next().contains('Building configuration...').scrollIntoView()
  })
})
