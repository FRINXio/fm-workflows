describe('Unmount VRP01 and netconf-testtool', function() { 
  beforeEach(function() {
    cy.login()
  })
	
  it('unmounts uncompatible devices', function() { 
    cy.visit('/') 
    cy.contains('UniConfig').click()	  
    cy.contains('VRP01').parent().find('td').eq(0).click()
    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('Unmount Devices').click()	  
    cy.contains('VRP01').should('not.to.exist')
    cy.contains('netconf-testtool').should('not.to.exist')
  })
})
