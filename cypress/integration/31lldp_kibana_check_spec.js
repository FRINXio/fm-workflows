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
    //cy.contains('Discover').click()	  
    //cy.get('div.kbnGlobalNavLink__title').click()
    //cy.get('div.iframes-container').click()
    cy.get('iframe').then(($iframe) => {
      const doc = $iframe.contents()
      //doc.contains('Discover').click(() => {
      doc.find('div.kbnGlobalNav__links > div > app-switcher > div.kbnGlobalNavLink > a').click(() => {
        console.log('clicked!!!!!!')
      })
      //cy.wrap(doc.contains('Discover')).click({force:true})
      //cy.wrap(doc.find('div.kbnGlobalNav__links > div > app-switcher > div.kbnGlobalNavLink > a')).click({force:true})
    })
  })

  it('goes to inventory', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/elasticsearch/_msearch?rest_total_hits_as_int=true&ignore_throttled=true').as('getSearchResults')
	  
    let inventory = Cypress.env('inventory')
    cy.visit(inventory)
    cy.url({timeout:5000}).should('include', '/app/')
    cy.contains('Discover',{timeout:10000}).click()
    cy.get('div.ui-select-match > span > i.caret.pull-right').click({force:true})
    //cy.contains('*lldp').click({force:true})
    cy.contains('inventory-lldp').click({force:true})
    cy.wait('@getSearchResults')
    //explicit wait
    cy.wait(500)
    cy.get('td').click({force:true,multiple:true})
    cy.get("dd span").contains('lldp').scrollIntoView()
  })
})
