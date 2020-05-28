//https://docs.frinx.io/frinx-machine/use-cases/save-and-run-command/save-and-run-command.html
//Save and execute commands on devices
describe('Save and execute commands on devices', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('Execute saved command on mounted devices', function() {
    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    //In our example we will use Execute_and_read_rpc_cli_device_from_inventory which will execute a command from inventory on one device without saving the output of this command to inventory.

    cy.visit('/')

    cy.contains('Workflows').click()
    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Execute_and_read_rpc_cli_device_from_inventory')
    cy.contains('Execute_and_read_rpc_cli_device_from_inventory').click()

    cy.screenshot()
    //this does not work because there are two workflows begening with the same string
    //cy.get('button[title="Execute"]').click()
    cy.get('#executeBtn-Execute_and_read_rpc_cli_device_from_inventory').click()

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
    cy.get('div.modal-header').contains('Details of Execute_and_read_rpc_cli_device_from_inventory',{timeout:30000})
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})

    cy.contains('Execution Flow').click()
    cy.get('#detailTabs-tabpane-execFlow').scrollIntoView()
    cy.wait(500) //wait - this element is detached from the DOM. - wait until attached

    //click the second one
    cy.get('g > rect').eq(1).click({force: true})
    cy.contains('Summary').click()
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('Summary').parent().parent().find('div > div > div.container > div.row').eq(4).find('code > pre').as('OutputBox')
    cy.get('@OutputBox').should(($json) => {
      expect($json, 'to expect to find in OUTPUT box of CLI_execute_and_read_rpc_cli (COMPLETED) workflow:').to.contain('interface Loopback')
      expect($json, 'to expect to find in OUTPUT box of CLI_execute_and_read_rpc_cli (COMPLETED) workflow:').to.contain('interface GigabitEthernet')
    })
    //scroll to view text interface ...
    //this will probably work only in FM v1.1 because in v1.2 output is automatically unescaped and "Unescape" button is removed
    cy.get('@OutputBox')
      .children().first()
      .children().first()
      .scrollTo('center', { duration: 1000 })
    cy.get('button.close').click()

    cy.contains('Input/Output').click()
    //curently Workflow Output "output": null - will be fixed
    //cy.contains('Workflow Output').parent().find('code').invoke('show').should('contain','"output": null')
    cy.contains('Workflow Output').parent().find('code').invoke('show').should('contain','interface GigabitEthernet')

    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
