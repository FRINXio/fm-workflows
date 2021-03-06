describe('Remove added devices', function () {

  //this test uses the pluggin @4tw/cypress-drag-drop
  it('creates workflow Remove_device_from_inventory', function () {
    //Remove_device_from_inventory
    //Tasks ... Search .... inventory -> INVENTORY_remove_device
    cy.server({
      method: 'POST',
    })
    cy.route('/uniflow/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('UniFlow').click()

    cy.url().should('include', '/uniflow/ui/defs')
    cy.contains('New').click()
    //cy.wait('@getWorkflowId')
    cy.contains('name:').parent().next().click().clear().type('Remove_device_from_inventory')
    cy.contains('Save').click()
    cy.get('a[title="Tasks"]').click()
    cy.get('input[placeholder="Search..."]').click().clear().type('INVENTORY_remove_device')

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
    cy.get('div.sidebar-content > a[draggable="true"]', { force: true })
      .drag('div.srd-node-layer', { force: true });

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

    cy.get('g > circle').next().contains('Start').parent().parent().parent().next().click().as('start')
    cy.get('div.port[data-nodeid="end"]').as('end')
    cy.get('div.srd-default-port--in').children('.port').first().as('in')
    cy.get('div.srd-default-port--out').children('.port').as('out')

    cy.get('@start')
      .trigger('mousedown', { which: 1 })
      //.trigger('mousemove', { force:true, clientX: 400 - 20, clientY: 300 })//this does not work
      .get('@in') //this works
      .trigger('mousemove')
      .trigger('mouseup', { force: true })

    cy.get('@out', { force: true })
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

  it('deletes GREATER_ONE_ROUTER', function () {
    cy.server({
      method: 'POST',
    })
    cy.route('/uniflow/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('UniFlow').click()

    cy.url().should('include', '/uniflow/ui/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Remove_device_from_inventory')
    cy.contains('Remove_device_from_inventory').click()
    cy.get('button[title="Execute"]').click()

    cy.get('label').contains('device_id').next().clear().type('GREATER_ONE_ROUTER')

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(3000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/uniflow/ui/exec')
    cy.get('div.modal-header').contains('Details of Remove_device_from_inventory', { timeout: 30000 })
    cy.get('div.headerInfo').contains('COMPLETED', { timeout: 10000 })

    cy.contains('Task Details').click()
    cy.contains('Input/Output').click()
    cy.contains('JSON').click()
    cy.contains('Edit & Rerun').click()

    cy.contains('Execution Flow').click()
    //click on the green box with the INVENTORY_remove_device text.
    cy.get('#detailTabs-tabpane-execFlow').scrollIntoView()
    //cy.contains('INVENTORY_remove_device').click() //this would work only with force:true because This element '<tspan>' is not visible because it has CSS property: 'position: fixed' and its being covered by another element:
    //here probably I need explicit wait because it used to time out - reason:
    //CypressError: Timed out retrying: cy.click() failed because this element is detached from the DOM.
    //<rect rx="5" ry="5" x="-61.34375" y="-27.5" width="122.6875" height="55" style="stroke: #48a770; fill: #48a770"></rect>
    //Cypress requires elements be attached in the DOM to interact with them.
    cy.wait(500) //wait - this element is detached from the DOM. - wait until attached
    cy.get('g > rect').click()
    cy.contains('INVENTORY_remove_device (COMPLETED)')
    cy.contains('Summary').click()
    //cy.contains('JSON').click() //this does not work - even in case of force true it finds lower one JSON link which was at previous modal window
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('JSON').click()
    cy.contains('Logs').click()
    cy.contains('Summary').click()
    cy.get('button.close').click()

    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })

  it('deletes BIG_ONE_ROUTER', function () {
    cy.server({
      method: 'POST',
    })
    cy.route('/uniflow/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/')

    cy.contains('UniFlow').click()

    cy.url().should('include', '/uniflow/ui/defs')
    cy.contains('Definitions').click() //there are three tabs: Definitions Executed and Scheduled
    cy.get('input[placeholder="Search by keyword."').type('Remove_device_from_inventory')
    cy.contains('Remove_device_from_inventory').click()
    cy.get('button[title="Execute"]').click()

    cy.get('label').contains('device_id').next().clear().type('BIG_ONE_ROUTER')

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(3000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click() //click the ID of the previously executed workflow to see the progress of the workflow

    cy.url().should('include', '/uniflow/ui/exec')
    cy.get('div.modal-header').contains('Details of Remove_device_from_inventory', { timeout: 30000 })
    cy.get('div.headerInfo').contains('COMPLETED', { timeout: 10000 })

    cy.contains('Task Details').click()
    cy.contains('Input/Output').click()
    cy.contains('JSON').click()
    cy.contains('Edit & Rerun').click()

    cy.contains('Execution Flow').click()
    //click on the green box with the INVENTORY_remove_device text.
    cy.get('#detailTabs-tabpane-execFlow').scrollIntoView()
    //cy.contains('INVENTORY_remove_device').click() //this would work only with force:true because This element '<tspan>' is not visible because it has CSS property: 'position: fixed' and its being covered by another element:
    //here probably I need explicit wait because it used to time out - reason:
    //CypressError: Timed out retrying: cy.click() failed because this element is detached from the DOM.
    //<rect rx="5" ry="5" x="-61.34375" y="-27.5" width="122.6875" height="55" style="stroke: #48a770; fill: #48a770"></rect>
    //Cypress requires elements be attached in the DOM to interact with them.
    cy.wait(500) //wait - this element is detached from the DOM. - wait until attached
    cy.get('g > rect').click()
    cy.contains('INVENTORY_remove_device (COMPLETED)')
    cy.contains('Summary').click()
    //cy.contains('JSON').click() //this does not work - even in case of force true it finds lower one JSON link which was at previous modal window
    cy.get('div[role="document"].modal-lg > div.modal-content > div.modal-body').contains('JSON').click()
    cy.contains('Logs').click()
    cy.contains('Summary').click()
    cy.get('button.close').click()

    cy.contains('Task Details').click()
    cy.contains('Close').scrollIntoView()
    cy.contains('Close').click()
  })

  it('deletes workflow Remove_device_from_inventory', function () {
    cy.visit('/')
    cy.contains('UniFlow').click()

    cy.url().should('include', '/uniflow/ui/defs')

    //here workflow Remove_device_from_inventoryshould be deleted
    cy.contains('UniFlow').click()
    cy.get('input[placeholder="Search by keyword."').type('Remove_device_from_inventory')
    cy.contains('Remove_device_from_inventory').click()
    cy.get('button[title="Delete"]').click()
    cy.get('button').contains('Delete').click()
  })

  it('Check Inventory', function () {
    let inventory = Cypress.env('inventory')
    cy.request({ url: inventory + "/inventory-device/_doc/BIG_ONE_ROUTER", failOnStatusCode: false }).should((req) => {
      expect(req.status).to.equal(404)
      expect(req.body.found).to.be.false
    })

    cy.request({ url: inventory + "/inventory-device/_doc/GREATER_ONE_ROUTER", failOnStatusCode: false }).should((req) => {
      expect(req.status).to.equal(404)
      expect(req.body.found).to.be.false
    })

  })
})
