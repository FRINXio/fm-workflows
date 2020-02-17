//https://docs.frinx.io/frinx-machine/use-cases/lldp-topology/lldp-topology.html
//Obtain LLDP topology data
//Collect LLDP Information from Devices and Build Topology
describe('Collect LLDP Information from Devices and Build Topology', function() {
  beforeEach(function() {
    cy.login()
  })
	

  it('collects LLDP Information from Devices', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    //In the following step we will start a workflow that goes to each mounted device, collects LLDP information, reconciles that information and finally stores that information in the inventory.
    cy.visit('/')

    cy.contains('UniConfig').click()
    cy.url().should('include', '/devices')
    cy.get('table tbody tr:nth-child(8)').should('to.exist')

    cy.get('.navbar-brand').click()	  
    cy.url().should('include', '/')
    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Build_read_store_LLDP_topology')	  
    cy.contains('Build_read_store_LLDP_topology').click()	  
    cy.get('button').contains('Execute').click()	  

    /*
    //	  
    cy.contains('').next().as('') //label  become alias of next input
    cy.get('@').type('{selectall}{backspace}')
    cy.get('@').type('')
    */

    //	  
    cy.contains('node-aggregation').next().as('node-aggregation') //label node-aggregation become alias of next input
    cy.get('@node-aggregation').type('{selectall}{backspace}')
    cy.get('@node-aggregation').type('system-name')

    //	  
    cy.contains('link-aggregation').next().as('link-aggregation') //label link-aggregation become alias of next input
    cy.get('@link-aggregation').type('{selectall}{backspace}')
    cy.get('@link-aggregation').type('bidirectional-abbreviations')

    //	  
    cy.contains('per-node-read-timeout').next().as('per_node_read_timeout') //label per_node_read_timeout become alias of next input
    cy.get('@per_node_read_timeout').type('{selectall}{backspace}')
    cy.get('@per_node_read_timeout').type('30')

    //	  
    cy.contains('concurrent-read-nodes').next().as('concurrent_read_nodes') //label concurrent_read_nodes become alias of next input
    cy.get('@concurrent_read_nodes').type('{selectall}{backspace}')
    cy.get('@concurrent_read_nodes').type('8')

    //	  
    cy.contains('destination-topology').next().as('destination_topology') //label destination_topology become alias of next input
    cy.get('@destination_topology').type('{selectall}{backspace}')
    cy.get('@destination_topology').type('lldp')

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Build_read_store_LLDP_topology',{timeout:30000})
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})

    cy.contains('Execution Flow').click()
    //click on the green box with the CLI_get_cli_journal text.
    cy.get('#detailTabs-tabpane-execFlow').scrollIntoView()
    cy.wait(500) //wait - this element is detached from the DOM. - wait until attached 
    //this stopped to work because Tomas added some test of presency and suddenly there are two rect's there 
    //cy.get('g > rect').click()
    //cy.contains('Build_read_store_LLDP_topology (COMPLETED)')
    //cy.contains('Summary').click()

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
