describe('Create workflow Read_journal_cli_device', function() { 
  beforeEach(function() {
    cy.login()

    //here workflow Read_journal_cli_device should be deleted
    /*
    cy.contains('Workflows').click()	  
    cy.get('input[placeholder="Search by keyword."').type('Read_journal_cli_device')	  
    cy.contains('Read_journal_cli_device').click()	  
    cy.get('button.btn-outline-danger').click()	  
    */
  })

	
  //TODO https://frinxhelpdesk.atlassian.net/browse/FM-353
  //TODO drag and drop in test does not work
  //TODO as a result that component are not properly connected saving process will fail
  //workaround: to import the neeeded workflow as json
  it('creates workflow', function() { 
    cy.server({
      method: 'POST',
    })
    cy.route('/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/') 

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')	  
    cy.contains('New').click()
    //cy.wait('@getWorkflowId')
    cy.contains('name:').parent().next().click().clear().type('Read_journal_cli_device')
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
    cy.get('div.sidebar-content > a[draggable="true"] > div').eq(1)
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 810, clientY: 330 })
      .trigger('mouseup', { force: true })
    cy.get('div.sidebar-content > a[draggable="true"]')
*/
    //https://github.com/4teamwork/cypress-drag-drop
    cy.get('div.sidebar-content > a[draggable="true"]',{force:true})
	  .drag('div.srd-node-layer',{force:true});
    cy.contains('In')
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { clientX: 400, clientY: 300 })
      .trigger('mouseup', { force: true })
/*
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
    cy.get('a[title="Tasks"]').click()

    cy.get('g > circle').next().contains('Start').parent().parent().next().click().as('start')
    cy.get('g > circle').next().contains('End').parent().parent().next().click().as('end')
    //cy.contains('CLI_get_cli_journal',{force:true}).click({force:true}).parent().next().find('div > div').click()
    cy.contains('In').prev().click().as('in')
    cy.contains('Out').next().click().as('out')

    cy.get('@start',{force:true})
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { force:true, clientX: 400 - 20, clientY: 300 })
      .trigger('mouseup', { force: true })

    cy.get('@end',{force:true})
      .trigger('mousedown', { which: 1 })
      .trigger('mousemove', { force:true, clientX: 600 - 135, clientY: 300 })
      .trigger('mouseup', { force: true })
/*
    cy.get('@start',{force:true}).drag('@in',{force:true})
    cy.get('@end',{force:true}).drag('@out',{force:true})
*/
    cy.get('button > i.save.icon').click()

  })

  //TODO workaround: to import the neeeded workflow as json
  //https://github.com/abramenal/cypress-file-upload
  it.skip('imports workflow', function() { 
    cy.visit('/') 

    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')	  
	 
    cy.contains('Import').click()	  

    cy.get('input[placeholder="Search by keyword."').type('Read_journal_cli_device')	  
    cy.contains('Read_journal_cli_device').click()	  
  })

})
