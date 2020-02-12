//https://docs.frinx.io/frinx-machine/use-cases/obtain-platform-inventory-data/obtain-platform-inventory-data.html
//Obtain platform inventory data
//Collect platform information from the device and store in the inventory
describe('Collect platform information from the device and store in the inventory', function() {
  beforeEach(function() {
    cy.login()
  })
	

  it('Collect', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('UniConfig').click()
    cy.url().should('include', '/devices')
    cy.get('table tbody tr:nth-child(8)').should('to.exist')

    cy.get('.navbar-brand').click()	  
    cy.url().should('include', '/')
    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Read_components_all_from_unified_update_inventory')	  
    cy.contains('Read_components_all_from_unified_update_inventory').click()	  
    //cy.contains('Read_components_update_inventory').click()	  
    cy.get('button').contains('Execute').click()	  

    cy.get('div.modal-content').contains('Execute').click()	  
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(3000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click()

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Read_components_all_from_unified_update_inventory',{timeout:30000})

    cy.contains('Execution Flow').click()
    cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:10000})

    cy.get('div[role="dialog"]').scrollTo('center', { duration: 1000 })
    cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('bottomRight', { duration: 1000 })
    cy.screenshot() 
    //cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('bottomLeft', { duration: 1000 })
    //cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('75%', '25%')
    //does not work cy.get('div.overflow.scroll').scrollTo('bottom', { duration: 5000 })

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
