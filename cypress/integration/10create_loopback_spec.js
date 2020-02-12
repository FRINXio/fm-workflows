describe('Create loopback address on devices stored in the inventory', function() { 
  beforeEach(function() {
    cy.login()

    //Make sure you didn’t skip mounting all devices in inventory, otherwise this workflow might not work correctly.
    //
    //This use case does not work with VRP01 and netconf-testtool devices. 
	  
    cy.visit('/') 
    cy.contains('UniConfig').click()	  
    cy.contains('VRP01').parent().find('td').eq(0).click()
    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('Unmount Devices').click()	  
    cy.contains('VRP01').should('not.to.exist')
    cy.contains('netconf-testtool').should('not.to.exist')
  })

	
  //prerequisite: not mounted VRP01 and netconf-testtool
  //TODO: this test fails if it is executed 2 times
  it('creates loopback700929 on all mounted devices', function() { 
    cy.server({
      method: 'POST',
    })
    cy.route('/api/conductor/workflow').as('getWorkflowId')

    cy.visit('/') 

    cy.contains('UniConfig').click() //look list of mounted devices  
    cy.get('table tbody tr:nth-child(8)').should('to.exist')

    cy.get('.navbar-brand').click()	  
    cy.contains('Workflows').click()	  

    cy.url().should('include', '/workflows/defs')	  
    cy.get('input[placeholder="Search by keyword."').type('Create_loopback_all_in_uniconfig')	  
    cy.contains('Create_loopback_all_in_uniconfig').click()	  
    cy.get('button').contains('Execute').click()
    cy.contains('loopback_id').parent().find('input').type('700929') //it should be random generated maybe

    cy.get('div.modal-content').contains('Execute').click()
    cy.wait('@getWorkflowId')
    cy.get('div.modal-content').contains('Execute').should('not.to.exist')
    cy.get('div.modal-content').contains('OK')
    //this explicit wait is needed to wait for completing of procesing on chain ConductorServer<->ElasticSearch<->Dyn
    cy.wait(3000)
    //hopufully now we are ready to go - let us click the workflow id link
    cy.get('div.modal-footer a:first-child').click()

    cy.url().should('include', '/workflows/exec')	  
    cy.get('div.modal-header').contains('Details of Create_loopback_all_in_uniconfig',{timeout:30000})
    cy.contains('Close').scrollIntoView()
    //cy.get('div.headerInfo').contains('COMPLETED',{timeout:40000})
	  
    //here there are some problem with visibility of table ...
    //cy.get('div.modal-content table tbody tr').should('have.length',2)
    //cy.get('#detailTabs-tabpane-taskDetails').get('tbody tr td:last').should('have.length',2)  ///.contains('COMPLETED',{timeout:300000})

    //here were again a lot of problems how to achieve clicking of subworkflow .... solutiion - invoke(show) on div which has set display:none:
    //cy.contains('Children').click().parent().find('div.dropdown-menu').invoke('show').contains('create_loopback').click()
    //^^^does not work in v1.1.0
    cy.contains('SUB_WORKFLOW').next().find('button').click()
    //cy.contains('create_loopback').click({force:true}) //this did not work
    //cy.contains('Children').click().get('a') // neither worked

    //cy.wait(5000)
    cy.contains('Details of Dynamic_fork')
    cy.contains('Close').scrollIntoView()
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:300000})
    cy.get('div.heightWrapper').scrollTo('bottom', { duration: 1000 })

    cy.contains('Input/Output').click()
    cy.contains('JSON').click()
    cy.contains('Edit & Rerun').click()
    cy.contains('Execution Flow').click()
    cy.get('#detailTabs-tabpane-execFlow > div').scrollTo('bottomRight', { duration: 1000 })
    cy.contains('Task Details').click()

    cy.contains('Parent').click()

    //return to previous
    cy.contains('Details of Create_loopback_all_in_uniconfig')
    //cy.contains('Children').click()
    //does not work in v1.1.0
	  
    cy.get('div.headerInfo').contains('COMPLETED',{timeout:300000})

    cy.contains('Input/Output').click()
    cy.contains('JSON').click()
    cy.contains('Edit & Rerun').click()
    cy.contains('Execution Flow').click()
    cy.contains('Task Details').click()

    cy.contains('Close').click()
    cy.get('span.navbar-brand a').click()

    cy.contains('UniConfig').click()	  

    cy.get('table tbody tr:nth-child(8)').should('to.exist')
	  	  
    //	  After the main and sub-workflows have completed successfully the loopback addres was created on the devices. Since we are working with emulated devices, we can check a device journal to see if it was really created.

  })
})
