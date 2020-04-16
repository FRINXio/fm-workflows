describe('Unmount netconf-testtool', function() { 
  beforeEach(function() {
    cy.login()
  })
	
  it('unmounts netconf-testtool', function() { 
    cy.server()
    cy.route('/api/odl/oper/all/status//topology-netconf').as('getAllStatusNetconf')

    cy.visit('/') 
    cy.contains('UniConfig').click()	  

    //wait a second for finishing of loading of the list of connected devices
    //there is two xhr we will wait for and after then 3 times bunch of xhrs
    cy.wait(['@getAllStatusNetconf']).then((xhrs) => {
      const netconfDev = xhrs.responseBody.topology[0].node
      const rowCount = ((netconfDev === undefined) ? 0 : netconfDev.length)
      cy.get('table tbody tr td:first-child', {timeout:5000}).should('have.length', rowCount)
    })

    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('Unmount Devices').click()	  

    cy.contains('netconf-testtool').should('not.to.exist')
  })
})
