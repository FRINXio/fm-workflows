//Note: this test is using virtual device accessible via VPN
//https://docs.frinx.io/frinx-machine/use-cases/add-to-inventory-and-mount/add-to-inventory-and-mount.html
//Mount the new device from Inventory
describe('Mount the new device from Inventory', function() {
  beforeEach(function() {
    cy.login()
  })
	

  it.skip('mount newly added cli device from the inventory', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Mount_from_inventory')	  
    cy.contains('Mount_from_inventory').click()	  
    cy.get('button').contains('Execute').click()	  

    var device_id='BIG_ONE_ROUTER' //: any unique identifier
    cy.get('label').contains('device_id').next().as('device_id') //label  become alias of next input
    cy.get('@device_id').type('{selectall}{backspace}')
    cy.get('@device_id').type(device_id)

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Mount_from_inventory',{timeout:30000})
    cy.contains('Execution Flow').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Execution Flow').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Input/Output').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Execution Flow').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('JSON').click()
    cy.contains('Close').scrollIntoView()
    //cy.get('div.headerInfo').contains('COMPLETED',{timeout:80000})

    cy.contains('Close').click()

    cy.get('.navbar-brand').click()	  
    cy.contains('UniConfig').click()	  
  })

  it.skip('mount newly added netconf device in the inventory', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Mount_from_inventory')	  
    cy.contains('Mount_from_inventory').click()	  
    cy.get('button').contains('Execute').click()	  

    var device_id='GREATER_ONE_ROUTER' //: any unique identifier
    cy.get('label').contains('device_id').next().as('device_id') //label  become alias of next input
    cy.get('@device_id').type('{selectall}{backspace}')
    cy.get('@device_id').type(device_id)

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Mount_from_inventory',{timeout:30000})
    cy.contains('Execution Flow').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Execution Flow').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Input/Output').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Execution Flow').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('JSON').click()
    cy.contains('Close').scrollIntoView()
    //cy.get('div.headerInfo').contains('COMPLETED',{timeout:80000})

    cy.contains('Close').click()

    cy.get('.navbar-brand').click()	  
    cy.contains('UniConfig').click()	  
  })
})
