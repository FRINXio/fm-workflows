//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices', function() {
  it('prepares index', function() {
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    //this is needed only for the first time
    //cy.contains('Explore on my own',{timeout:10000}).click()
    cy.contains('Management',{timeout:20000}).click()
    cy.contains('Index Patterns',{timeout:10000}).click({force:true})
    cy.get('button[data-test-subj="createIndexPatternButton"]').click({force:true})
    cy.get('input[name="indexPattern"][data-test-subj="createIndexPatternNameInput"]').clear({force:true}).type('inventory-show_cmd{del}',{force:true})
    cy.contains('Success! Your index pattern matches 1 index.')
    cy.contains('Next step',{timeout:10000}).click({force:true})
    cy.get('button[data-test-subj="createIndexPatternCreateButton"]').contains('Create index pattern',{timeout:10000}).click({force:true})
    //explicit wait - occasionally I quit too quick - before successful creating of index !!!
    cy.wait(500)
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
    cy.contains('Discover',{timeout:10000}).click()
    //cy.get('div.ui-select-match > span > i.caret.pull-right').click({force:true})
    cy.get('i.caret.pull-right').click({force:true})
    cy.contains('inventory-show_cmd').click({force:true})
    cy.wait('@getSearchResults')
    //explicit wait
    //here was in jenkins regular fail of this test - I am forced to solve that by so high value of wait time !!!!
    cy.wait(2000)
    //let us try instead of explicite wait this
    //cy.get('table tbody tr:nth-child(1)').should('to.exist')
    //cy.get('td').click({force:true,multiple:true})
    cy.get('td[data-test-subj="docTableExpandToggleColumn"]').click({force:true,multiple:true})
    cy.get("dd span").contains('show_command').scrollIntoView()
  })
}) 
