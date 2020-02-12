describe('setup kibana', function() {
  it('being FIRST TIME IN KIBANA prepare indices', function() {
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    //this is needed only for the first time
    cy.contains('Explore on my own',{timeout:10000}).click()
    cy.contains('Management',{timeout:10000}).click()
    cy.contains('Index Patterns',{timeout:10000}).click({force:true})
    cy.get('button[data-test-subj="createIndexPatternButton"]').click({force:true})
    cy.get('input[name="indexPattern"][data-test-subj="createIndexPatternNameInput"]').clear({force:true}).type('logstash',{force:true})
    cy.contains('Success! Your index pattern matches 1 index.')
    cy.contains('Next step',{timeout:10000}).click({force:true})
    //cy.contains('Show advanced options',{timeout:10000}).click({force:true})
    cy.get('select[data-test-subj="createIndexPatternTimeFieldSelect"]').select("I don't want to use the Time Filter",{force:true})
    cy.get('button[data-test-subj="createIndexPatternCreateButton"]').contains('Create index pattern',{timeout:10000}).click({force:true})
  })
})
