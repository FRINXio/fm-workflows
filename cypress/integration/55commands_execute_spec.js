//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('Execute saved command on mounted devices', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    //In our example we will use Execute_all_from_cli_update_inventory which will execute a command from inventory on one device without saving the output of this command to inventory.

    cy.visit('/')

    cy.contains('Workflows').click()	  
    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Execute_all_from_cli_update_inventory')	  
    cy.contains('Execute_all_from_cli_update_inventory').click()	  

    cy.get('button').contains('Execute').click()	  

    cy.contains('template_id').next().as('template_id') //label bundle_ether_id become alias of next input
    cy.get('@template_id').type('{selectall}{backspace}')
    cy.get('@template_id').type('sh_run')

    cy.contains('params').next().as('params') //label bundle_ether_id become alias of next input
    cy.get('@params').type('{selectall}{backspace}')
    //cy.get('@params').type('')

    cy.get('div.modal-content > div.modal-footer').contains('Execute').click()	  
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content > div.modal-footer').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content > div.modal-footer').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Execute_all_from_cli_update_inventory',{timeout:30000})
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})

    cy.contains('Task Details').click()

    // ### GOING TO SUB_WORKFLOW ###
    cy.get('td').contains(/^2$/).next().next().find('button').click()
    cy.get('div.modal-header').contains('Details of Dynamic_fork',{timeout:30000})
    cy.contains('Execution Flow').click()
    cy.contains('Task Details').click()
    //     ### GOING TO SUB_WORKFLOW ###
    cy.get('td').contains(/^2$/).next().next().find('button').click()
    cy.get('div.modal-header').contains('Details of Execute_and_read_rpc_cli_device_from_inventory_update_inventory',{timeout:30000})
    cy.contains('Parent').click()
    cy.get('div.modal-header').contains('Details of Dynamic_fork',{timeout:30000})
    //     ### LEAVING SUB_WORKFLOW ###
    cy.contains('Parent').click()
    // ### LEAVING SUB_WORKFLOW ###

    cy.get('div.modal-header').contains('Details of Execute_all_from_cli_update_inventory',{timeout:30000})

    cy.contains('Task Details').click()

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
