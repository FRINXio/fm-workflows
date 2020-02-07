//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices', function() {
  it('goes to inventory', function() {
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
    cy.wait(500)
    cy.get('td').click({force:true,multiple:true})
    cy.get("dd span").contains('show_command').scrollIntoView()
  })
}) 
