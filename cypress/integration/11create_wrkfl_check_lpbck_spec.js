describe('Create workflow test it and finally delete it', function() { 
  beforeEach(function() {
    cy.login()
  })

  //this test uses the pluggin @4tw/cypress-drag-drop
  it('creates workflow Read_journal_cli_devicei_TEST', function() { 
    cy.server({
      method: 'POST',
    })
    cy.route('/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/') 

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')	  
    cy.contains('New').click()
    //cy.wait('@getWorkflowId')
    cy.contains('name:').parent().next().click().clear().type('Read_journal_cli_device_TEST')
    cy.contains('Save').click()
    cy.get('a[title="Tasks"]').click()
    cy.get('input[placeholder="Search..."]').click().clear().type('CLI_get_cli_journal')

    cy.get('g > circle').next().contains('Start')
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 200, clientY: 300 })
      .trigger('mouseup', { force: true })

    cy.get('g > circle').next().contains('End')
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 600, clientY: 300 })
      .trigger('mouseup', { force: true })

    /*
    cy.get('div.sidebar-content > a[draggable="true"] > div > i')
    cy.get('div.sidebar-content > a[draggable="true"] > div').first()
    //this does not work
    cy.get('div.sidebar-content > a[draggable="true"] > div').eq(1)
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 810, clientY: 330 })
      .trigger('mouseup', { force: true })
    */

    //it works with pluggin @4tw/cypress-drag-drop
    cy.get('div.sidebar-content > a[draggable="true"]',{force:true})
	  .drag('div.srd-node-layer',{force:true});

    //this works without pluggin support but only on the editor canvas
    cy.contains('In')
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 400, clientY: 300 })
      .trigger('mouseup', { force: true })

    /*
    //this does not work
    cy.get('div.sidebar-content > a[draggable="true"] > div > i')
      .trigger("dragstart")
    cy.get('div.srd-node-layer')
      .trigger("drop")
    //Uncaught TypeError: Cannot read property 'setData' of undefined

	  
    //https://github.com/cypress-io/cypress/issues/649
    var MyDataTransfer = function () {};
    var dt = new MyDataTransfer ();
    dt.types = [];

    cy.get('div.sidebar-content > a[draggable="true"] > div > i')
      .trigger("dragstart", {dataTransfer: dt})
    cy.get('div.srd-node-layer')
      .trigger("drop", {dataTransfer: dt})
    */

    cy.get('a[title="Tasks"]').click() //hide the left sidebar

    /*
    //this does not work
    cy.get('g > circle').next().contains('Start').parent().parent().next().click().as('start')
    cy.get('g > circle').next().contains('End').parent().parent().next().click().as('end')
    cy.contains('In').prev().click().as('in')
    cy.contains('Out').next().click().as('out')
    */

    cy.get('g > circle').next().contains('Start').parent().parent().next().click().as('start')
    cy.get('div.port[data-nodeid="end"]').as('end')    
    cy.get('div.srd-default-port--in').children('.port').first().as('in')
    cy.get('div.srd-default-port--out').children('.port').as('out')

    cy.get('@start')
      .trigger('mousedown', { which: 1 })
      //.trigger('mousemove', { force:true, clientX: 400 - 20, clientY: 300 })//this does not work
      .get('@in') //this works
      .trigger('mousemove')
      .trigger('mouseup', { force: true })

    cy.get('@out',{force:true})
      .trigger('mousedown', { which: 1 })
      //.trigger('mousemove', { force:true, clientX: 600 - 135, clientY: 300 })//this does not work
      .get('@end') //this works
      .trigger('mousemove')
      .trigger('mouseup', { force: true })

    /*
    //this does not work
    cy.get('@start',{force:true}).drag('@in',{force:true})
    cy.get('@end',{force:true}).drag('@out',{force:true})
    */

    cy.get('button > i.save.icon').click()
  })

  it('retrieves journal for XR02', function() {
    cy.server({
      method: 'POST',
    })
    cy.route('/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('UniConfig').click()

    cy.url().should('include', '/devices')
    cy.get('table tbody tr').first().find('td').eq(1).should('contain','XR02')
    cy.get('td#node_id-0').contains('XR02')
    //TODO how to put it into variable?

    cy.get('.navbar-brand').click()	  
    cy.url().should('include', '/')
    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Read_journal_cli_device_TEST')	  
    cy.contains('Read_journal_cli_device_TEST').click()	  
    cy.get('button').contains('Execute').click()	  
	  
    //label device_id
    //this is input with autocompletion	  
    //at first try to click it to see the list of devices
    //then try to choose one e.g. the first like user would do
    //cy.contains('device_id').parent().find('input').type('XR02').clear() //this does not work because there are two inputs - one for autocompletion...
    //cy.get('input[placeholder="Enter the node id"').click() //this is input with autocompletion	  
    //cy.get('input[placeholder="Enter the node id"').clear().type('XR07') //this is input with autocompletion	  
    //cy.contains('No matches found')
    //TODO Execute
    //negative test abrakadabra -> No matches found .... try to execute - this will break page
    //cy.get('input[placeholder="Enter the node id"').clear().type('XR02') //this is input with autocompletion	  
    //cy.get('input[placeholder="Enter the node id"').clear().click() //this is input with autocompletion	  
    //cy.contains('XR02').click()
    cy.get('label').contains('device_id').next().clear().type('XR02')

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(3000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow
	  
    //TODO skusit dat do premennej
    //click the ID of the previously executed workflow to see the progress of the workflow
    //http://localhost:3000/workflows/exec/bdc20041-0aec-44da-bf69-672d492f1210
    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Read_journal_cli_device',{timeout:30000})
    cy.get('div.headerInfo').contains('COMPLETED')

    cy.contains('Task Details').click()
    cy.contains('Input/Output').click()
	  
    //The journal information can be found in the output of the workflow
    cy.contains('Workflow Output').parent().contains('Unescape').click()
    //cy.scrollTo('bottom') // this does not work failed because this element is not scrollable <window>
    //search for interface Loopback700929
    //TODO here code is found 2x one of the found element is hidden - try to identify/locate element unambiguously
    cy.contains('Workflow Output').parent().find('code').invoke('show').should('contain','interface Loopback700929') //problem element code is not visible (more exact told one is visible and the second one is hidden)
    cy.get('div[role="document"]:not(.modal-lg)').contains('Workflow Output').parent().find('code').should('contain','interface Loopback700929')
    //Workflow Output  parent() is h4 ... > button with text Escape 
    cy.contains('Workflow Output').parent().contains('Escape').click()

    cy.contains('JSON').click()
    cy.contains('Edit & Rerun').click()

    cy.contains('Execution Flow').click()
    //click on the green box with the CLI_get_cli_journal text.
    cy.get('#detailTabs-tabpane-execFlow').scrollIntoView()
    //cy.contains('CLI_get_cli_journal').click() //this would work only with force:true because This element '<tspan>' is not visible because it has CSS property: 'position: fixed' and its being covered by another element:
    //here probably I need explicit wait because it used to time out - reason:
    //CypressError: Timed out retrying: cy.click() failed because this element is detached from the DOM.
    //<rect rx="5" ry="5" x="-61.34375" y="-27.5" width="122.6875" height="55" style="stroke: #48a770; fill: #48a770"></rect>
    //Cypress requires elements be attached in the DOM to interact with them.
    cy.wait(500) //wait - this element is detached from the DOM. - wait until attached 
    cy.get('g > rect').click()
    cy.contains('CLI_get_cli_journal (COMPLETED)')
    cy.contains('Summary').click()
    //cy.contains('JSON').click() //this does not work - even in case of force true it finds lower one JSON link which was at previous modal window
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('JSON').click()
    cy.contains('Logs').click()
    cy.contains('Summary').click()

    //The journal information can be found in the output of the workflow
    //cy.get('div.container > div.row').eq(5).contains('Unescape').click() // obviously there are counted also elements in previous modal window because if I count what I see in above modal window it is on 3rd position
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('Summary').parent().parent().find('div > div > div.container > div.row').eq(3).contains('Unescape').click()
    //search for interface Loopback700929
    //cy.get('code').invoke('show').should('contain','interface Loopback700929') //problem element code is not visible // not sure which one I located here It is difficult to craft good path
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('Summary').parent().parent().find('div > div > div.container > div.row').eq(4).find('code > pre').should('contain','interface Loopback700929')

    cy.get('button.close').click()

    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })

  it('deletes workflow Read_journal_cli_devicei_TEST', function() { 
    //here workflow Read_journal_cli_device_TEST should be deleted
    cy.contains('Workflows').click()	  
    cy.get('input[placeholder="Search by keyword."').type('Read_journal_cli_device_TEST')	  
    cy.contains('Read_journal_cli_device_TEST').click()	  
    cy.get('button.btn-outline-danger').click()	  
  })
	
  //TODO make a test: to import the neeeded workflow as json
  //TODO workaround: to import the neeeded workflow as json
  //https://github.com/abramenal/cypress-file-upload
  //file to be imported will be in fixtures folder
  it.skip('imports workflow', function() { 
    cy.visit('/') 

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')	  
	 
    cy.contains('Import').click()	  

    cy.get('input[placeholder="Search by keyword."').type('Read_journal_cli_device')	  
    cy.contains('Read_journal_cli_device').click()	  
  })
})
