//https://docs.frinx.io/frinx-machine/use-cases/lldp-topology/lldp-topology.html
//Obtain LLDP topology data
//Collect LLDP Information from Devices and Build Topology
describe('Collect LLDP Information from Devices and Build Topology', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('exports the IETF topology information in graphviz format', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    //Exporting the IETF topology information in graphviz format
    cy.visit('/')

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Export_LLDP_topology')	  
    cy.contains('Export_LLDP_topology').click()	  
    cy.get('button').contains('Execute').click()	  

    cy.get('div.modal-content').contains('Execute').click()	  
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Export_LLDP_topology',{timeout:3000})
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED')

    cy.contains('Input/Output').click()
    //TODO
    //cy.contains('Workflow Output').parent().find('code > pre#wfoutput').invoke('show').type('{selectall}{ctrl}c')
    cy.contains('Workflow Output').parent().find('code > pre#wfoutput').then(($code) => {
      const txt = $code.text() 
      console.log(txt)
      cy.writeFile('cypress/fixtures/lldp_export.json', txt)
    })
    //cy.contains('Workflow Output').parent().contains('Escape').click()

    cy.contains('Execution Flow').click()
    //click on the green box with the CLI_get_cli_journal text.
    cy.get('#detailTabs-tabpane-execFlow').scrollIntoView()
    cy.wait(500) //wait - this element is detached from the DOM. - wait until attached 
    cy.get('g > rect').click()
    cy.contains('LLDP_export_topology (COMPLETED)')
    cy.contains('Summary').click()
    //so simple as reffering e.g. Summary does not work for JSON tab...
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('JSON').click()
    cy.contains('Logs').click()
    cy.contains('Summary').click()
    //TODO
    //cy.get('code').invoke('show').type('{selectall}{ctrl}c')

    cy.get('button.close').click()

    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
