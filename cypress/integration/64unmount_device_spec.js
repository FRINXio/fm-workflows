describe('Unmount added devices', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('unmounts devices', function() {
    cy.server()
    cy.route('/api/odl/oper/all/status/cli').as('getAllStatusCli')
    cy.route('/api/odl/oper/all/status/topology-netconf').as('getAllStatusNetconf')

    cy.visit('/')
    cy.contains('UniConfig').click()

    //20200514
    //THIS WORKS ON SLOWER NETWORKS BUT NOT LOCALLY
    //WHEN RUNNING FM ON localhost THEN THESE XHRs ARE TOO FAST TO CATCH
    //wait a second for finishing of loading of the list of connected devices
    //there is two xhr we will wait for and after then 3 times bunch of xhrs
    //cy.wait(['@getAllStatusCli', '@getAllStatusNetconf']).then((xhrs) => {
    //  const cliDev = xhrs[0].responseBody.topology[0].node
    //  const netconfDev = xhrs[1].responseBody.topology[0].node
    //  const rowCount = ((cliDev === undefined) ? 0 : cliDev.length) + ((netconfDev === undefined) ? 0 : netconfDev.length)
    //  cy.get('table tbody tr td:first-child', {timeout:5000}).should('have.length', rowCount)
    //})
    cy.waitForXHR('@getAllStatusCli', '@getAllStatusNetconf')

    var device_id1='BIG_ONE_ROUTER'
    cy.contains(device_id1).parent().find('td').eq(0).find('div input').click()
    cy.contains('Unmount Devices').click()
    var device_id2='GREATER_ONE_ROUTER'
    cy.contains(device_id2).parent().find('td').eq(0).find('div input').click()
    cy.contains('Unmount Devices').click()

    cy.contains(device_id1).should('not.to.exist')
    cy.contains(device_id2).should('not.to.exist')
  })

  it.skip('unmounts netconf device GREATER_ONE_ROUTER via workflow', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/api/conductor/workflow').as('getWorkflowId')
    cy.visit('/')

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Unmount_netconf_device')	  
    cy.contains('Unmount_netconf_device').click()	  
    cy.get('button').contains('Execute').click()	  
    cy.contains('device_id').next().as('device_id') //label bundle_ether_id become alias of next input
    cy.get('@device_id').type('{selectall}{backspace}')
    cy.get('@device_id').type('GREATER_ONE_ROUTER').find('li[aria-label="GREATER_ONE_ROUTER"]').click()

    cy.get('div.modal-content').contains('Execute').click()	  
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Unmount_netconf_device',{timeout:30000})
    cy.get('div.headerInfo').contains('COMPLETED')

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })

  it.skip('unmounts cli device BIG_ONE_ROUTER via workflow', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/api/conductor/workflow').as('getWorkflowId')
    cy.visit('/')

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Unmount_cli_device')	  
    cy.contains('Unmount_cli_device').click()	  
    cy.get('button').contains('Execute').click()	  
    cy.contains('device_id').next().as('device_id') //label bundle_ether_id become alias of next input
    cy.get('@device_id').type('{selectall}{backspace}')
    cy.get('@device_id').type('BIG_ONE_ROUTER').find('li[aria-label="BIG_ONE_ROUTER"]').click()

    cy.get('div.modal-content').contains('Execute').click()	  
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(1000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Unmount_cli_device',{timeout:30000})
    cy.get('div.headerInfo').contains('COMPLETED')

    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })
})
