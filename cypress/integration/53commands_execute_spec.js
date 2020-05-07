//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('Execute saved command on mounted devices', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    //In our example we will use Execute_and_read_rpc_cli_device_from_inventory_update_inventory which will execute a command from inventory on one device without saving the output of this command to inventory.

    cy.visit('/')

    cy.contains('Workflows').click()	  
    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Execute_and_read_rpc_cli_device_from_inventory_update_inventory')	  
    cy.contains('Execute_and_read_rpc_cli_device_from_inventory_update_inventory').click()	  

    cy.get('button').contains('Execute').click()	  

    cy.contains('template_id').next().as('template_id') //label bundle_ether_id become alias of next input
    cy.get('@template_id').type('{selectall}{backspace}')
    cy.get('@template_id').type('sh_run')

    cy.contains('device_id').next().as('device_id') //label bundle_ether_id become alias of next input
    cy.get('@device_id').type('{selectall}{backspace}')
    //cy.get('@device_id').type('IOS01') //bug FM-364
    //cy.get('@device_id').type('IOS01').find('li[aria-label="IOS01"] a').contains('IOS01').click()
    cy.get('@device_id').type('IOS01').find('li[aria-label="IOS01"]').click()


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
    cy.get('div.modal-header').contains('Details of Execute_and_read_rpc_cli_device_from_inventory_update_inventory',{timeout:30000})
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})

    cy.contains('Task Details').click()

    // ### GOING TO SUB_WORKFLOW ###
    cy.get('td').contains(/^1$/).next().next().find('button').click()
    cy.get('div.modal-header').contains('Details of Execute_and_read_rpc_cli_device_from_inventory',{timeout:30000})

    cy.get('td').contains(/^2$/).next().contains('CLI_execute_and_read_rpc_cli').click()
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('Summary').parent().parent().find('div > div > div.container > div.row').eq(4).find('code > pre').as('OutputBox')
    cy.get('@OutputBox').should(($json) => {
      expect($json, 'to expect to find in OUTPUT box of CLI_execute_and_read_rpc_cli (COMPLETED) workflow:').to.contain('interface Loopback')
      expect($json, 'to expect to find in OUTPUT box of CLI_execute_and_read_rpc_cli (COMPLETED) workflow:').to.contain('interface GigabitEthernet')
    })
    cy.get('button.close').click()
    cy.contains('Parent').click()
    // ### LEAVING SUB_WORKFLOW ###

    cy.get('div.modal-header').contains('Details of Execute_and_read_rpc_cli_device_from_inventory_update_inventory',{timeout:30000})

    cy.contains('Task Details').click()
    cy.get('td').contains(/^2$/).next().contains('INVENTORY_add_field_to_device').click()
    cy.contains('INVENTORY_add_field_to_device (COMPLETED)')
    //TODO in Input Box there is a new field sh_run but its value is set to null 
    cy.contains('Summary').click()
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('Summary').parent().parent().find('div > div > div.container > div.row').eq(2).find('code > pre').as('InputBox')
    cy.get('@InputBox').should(($json) => {
      expect($json, 'to expect to find in INPUT box of INVENTORY_add_field_to_device (COMPLETED) workflow:').to.contain('interface Loopback')
      expect($json, 'to expect to find in INPUT box of INVENTORY_add_field_to_device (COMPLETED) workflow:').to.contain('interface GigabitEthernet')
    })
    cy.get('button.close').click()

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
