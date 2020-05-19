//https://docs.frinx.io/frinx-machine/use-cases/lldp-topology/lldp-topology.html
//Obtain LLDP topology data
//Collect LLDP Information from Devices and Build Topology
describe('Collect LLDP Information from Devices and Build Topology', function() {
  it.skip('goes to inventory (via iframe)', function() {
    //After the workflow has completed, go to Kibana and look for an entry called “lldp”. 
    cy.get('.navbar-brand').click()	  
    cy.url().should('include', '/')
    cy.contains('Inventory & Logs').click()	  
    cy.url().should('include', '/inventory')

    cy.wait(5000)
    //https://github.com/cypress-io/cypress/issues/136#issuecomment-328100955
    //cy.contains('Discover',{timeout:20000}).click()	  
    //cy.get('div.kbnGlobalNavLink__title').click()
    //cy.get('div.iframes-container').click()
    cy.get('iframe').then(($iframe) => {
      const doc = $iframe.contents()
      //doc.contains('Discover',{timeout:20000}).click(() => {
      doc.find('div.kbnGlobalNav__links > div > app-switcher > div.kbnGlobalNavLink > a').click(() => {
        console.log('clicked!!!!!!')
      })
      //cy.wrap(doc.contains('Discover',{timeout:20000})).click({force:true})
      //cy.wrap(doc.find('div.kbnGlobalNav__links > div > app-switcher > div.kbnGlobalNavLink > a')).click({force:true})
    })
  })

  it('prepares index', function() {
    cy.server()
    cy.route('**?pattern=inventory-lldp&**').as('getXhr')
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    //this is needed only for the first time
    //cy.contains('Explore on my own',{timeout:10000}).click()
    cy.contains('Management',{timeout:20000}).click()
    cy.contains('Index Patterns',{timeout:10000}).click({force:true})
    cy.get('button[data-test-subj="createIndexPatternButton"]').click({force:true})
    cy.get('input[name="indexPattern"][data-test-subj="createIndexPatternNameInput"]').clear({force:true}).type('inventory-lldp{del}',{force:true})
    cy.contains('Success! Your index pattern matches 1 index.')
    cy.contains('Next step',{timeout:10000}).click({force:true})
    cy.wait('@getXhr')
    cy.get('button[data-test-subj="createIndexPatternCreateButton"]').contains('Create index pattern',{timeout:10000}).click({force:true})
    cy.contains('Creating index pattern…')
    cy.contains('inventory-lldp')
  })

  it('retrieves data', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/elasticsearch/_msearch?rest_total_hits_as_int=true&ignore_throttled=true').as('getSearchResults')
	  
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    cy.contains('Discover',{timeout:20000}).click()
    cy.get('div.ui-select-match > span > i.caret.pull-right').click({force:true})
    //cy.contains('*lldp').click({force:true})
    cy.contains('inventory-lldp').click({force:true})
    cy.wait('@getSearchResults')
    //explicit wait
    cy.wait(500)
    cy.get('td').click({force:true,multiple:true})
    cy.get("dd span").contains('lldp').scrollIntoView()
    cy.get("dd span").contains('link').scrollIntoView()
    cy.get("dd span").contains('source').scrollIntoView()
    cy.get("dd span").contains('destination').scrollIntoView()
    cy.get("dd span").contains('termination-point').scrollIntoView()
  })
})
