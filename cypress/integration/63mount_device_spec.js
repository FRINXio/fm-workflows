//Note: this test is using virtual device accessible via VPN
//https://docs.frinx.io/frinx-machine/use-cases/add-to-inventory-and-mount/add-to-inventory-and-mount.html
//Mount the new device from Inventory
describe('Mount the new device from Inventory', function() {
  beforeEach(function() {
    cy.login()
  })
	

  it('mount newly added cli device from the inventory', function() {
    var device_id='BIG_ONE_ROUTER' //: any unique identifier

    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')
    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfigC')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfigO')

    cy.visit('/')

    cy.contains('Workflows').click()

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Mount_from_inventory')
    cy.contains('Mount_from_inventory').click()	
    cy.get('button').contains('Execute').click()

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
    cy.contains('Execution Flow').click()
    //cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:80000})

    cy.contains('Close').click()

    cy.get('.navbar-brand').click()
    cy.contains('UniConfig').click()
    cy.contains(device_id,{timeout:10000}).parent().find('td').eq(0).click()
    cy.contains(device_id).parent().find('td').eq(3).contains('connected')
    //20200518THIS WORKED IN V1.1 BUT STOPPED TO WORK IN V1.2 DUE TO CHANGE OF CLASS (ALIGN CENTER-> ALIGN LEFT)
    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    //20200518 wait only for the second xhr
    //cy.wait('@getConfigC')
    cy.wait('@getConfigO')
    cy.url().should('include', '/devices/edit/' + device_id)
  })

  it('try to mount already MOUNTED newly added cli device from the inventory', function() {
    var device_id='BIG_ONE_ROUTER' //: any unique identifier

    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('Workflows').click()

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Mount_from_inventory')
    cy.contains('Mount_from_inventory').click()	
    cy.get('button').contains('Execute').click()

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
    cy.contains('Execution Flow').click()
    //cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('FAILED',{timeout:80000})

    cy.contains('Close').click()

    cy.get('.navbar-brand').click()
    cy.contains('UniConfig').click()
    cy.contains(device_id,{timeout:10000}).parent().find('td').eq(0).click()
    cy.contains(device_id).parent().find('td').eq(3).contains('connected')
  })

  it('mount newly added netconf device in the inventory', function() {
    var device_id='GREATER_ONE_ROUTER' //: any unique identifier

    cy.server()
    cy.route('POST', '/api/conductor/workflow').as('getWorkflowId')
    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfigC')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfigO')

    cy.visit('/')

    cy.contains('Workflows').click()

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Mount_from_inventory')
    cy.contains('Mount_from_inventory').click()	
    cy.get('button').contains('Execute').click()

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
    //cy.contains('Execution Flow').click()
    //cy.contains('Close').scrollIntoView()
    //cy.contains('Task Details').click()
    //cy.contains('Close').scrollIntoView()
    //cy.contains('Execution Flow').click()
    //cy.contains('Close').scrollIntoView()
    //cy.contains('Input/Output').click()
    //cy.contains('Close').scrollIntoView()
    cy.contains('Execution Flow').click()
    ////cy.contains('Close').scrollIntoView()
    //cy.contains('JSON').click()
    //cy.contains('Close').scrollIntoView()
    cy.get('div[role="dialog"]').scrollTo('bottom', { duration: 1000 })
    ////cy.contains('Execution Flow').click()
    ////cy.contains('Close').scrollIntoView()

    //this ended with:
    // CypressError: Timed out retrying: Expected to find content: 'COMPLETED' within the element: <div.headerInfo> but never did.
    //cy.get('div.headerInfo').contains('COMPLETED',{timeout:180000})
    cy.wait(60000)

    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Input/Output').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('JSON').click()
    cy.contains('Close').scrollIntoView()

    cy.contains('Close').click()

    cy.get('.navbar-brand').click()
    cy.contains('UniConfig').click()
    cy.contains(device_id,{timeout:1000000}).parent().find('td').eq(0).click()
    cy.contains(device_id).parent().find('td').eq(3).contains('connected',{timeout:180000})
    //20200518THIS WORKED IN V1.1 BUT STOPPED TO WORK IN V1.2 DUE TO CHANGE OF CLASS (ALIGN CENTER-> ALIGN LEFT)
    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    //20200518 wait only for the second xhr
    //cy.wait('@getConfigC')
    cy.wait('@getConfigO')
    cy.url().should('include', '/devices/edit/' + device_id)
  })
})
