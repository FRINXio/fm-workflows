//https://docs.frinx.io/frinx-machine/use-cases/lacp/lacp.html
//This workflow is using uniconfig to create LAG interface on two nodes and assigns the bundle id to given interfaces on both nodes.
describe('LACP workflows', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('checks if ios-xr devices are mounted', function() {
    cy.visit('/')

    cy.contains('UniConfig').click()
    cy.url().should('include', '/devices')

    cy.get('table tbody tr:nth-child(8)').should('to.exist')
    cy.get('table tbody tr').first().should('contain','ios xr')
    cy.get('table tbody tr').eq(1).should('contain','ios xr') //the second row
  })

  it('creating a link aggregation between two nodes', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    cy.get('.navbar-brand').click()	  
    cy.url().should('include', '/')
    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Link_aggregation')	  
    cy.contains('Link_aggregation').click()	  
    cy.contains('Input').click()	  

    cy.contains('node1').next().click() //label node1
    //cy.contains('node1').next().type('sss').clear() //label node1 // I tried to clear div element - not possible
    cy.contains('node1').next().type('{selectall}{backspace}')
    cy.contains('XR01').click()

    cy.contains('bundle_ether_id').next().as('bundle_ether_id') //label bundle_ether_id become alias of next input
    cy.get('@bundle_ether_id').type('{selectall}{backspace}')
    cy.get('@bundle_ether_id').type('3')

    cy.contains('bundle_ether_enabled').next().as('bundle_ether_enabled') //label bundle_ether_enabled become alias of next input
    cy.get('@bundle_ether_enabled').type('{selectall}{backspace}')
    cy.get('@bundle_ether_enabled').type('true')

    cy.contains('node2').next().as('node2') //label node2 become alias for next input
    cy.get('@node2').type('{selectall}{backspace}')
    cy.contains('XR02').click() //choose from autocomplete combo box by clicking

    cy.contains('node1_ifaces').next().as('node1_ifaces') //label node1_ifaces become alias of next input
    cy.get('@node1_ifaces').type('{selectall}{backspace}')
    cy.get('@node1_ifaces').type('GigabitEthernet0/0/0/0, GigabitEthernet0/0/0/1')

    cy.contains('node2_ifaces').next().as('node2_ifaces') //label node2_ifaces become alias of next input
    cy.get('@node2_ifaces').type('{selectall}{backspace}')
    cy.get('@node2_ifaces').type('GigabitEthernet0/0/0/1, GigabitEthernet0/0/0/2, GigabitEthernet0/0/0/3')

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Link_aggregation',{timeout:3000})
    //cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})
    //instead of waiting to COMPLETED try to examine process running e.g. on Execution Flow tab

    cy.contains('Execution Flow').click()
    cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})

    cy.get('div[role="dialog"]').scrollTo('center', { duration: 1000 })
    cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('bottomRight', { duration: 1000 })
    //cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('bottomLeft', { duration: 1000 })
    //cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('75%', '25%')
    //does not work cy.get('div.overflow.scroll').scrollTo('bottom', { duration: 5000 })

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
