describe('Unmount all mounted devices', function() {
  beforeEach(function() {
    cy.login()
  })
	
  it('unmounts all devices', function() {
    cy.server()
    cy.route('/uniconfig/api/uniconfig/oper/all/status/cli').as('getAllStatusCli')
    cy.route('/uniconfig/api/uniconfig/oper/all/status/topology-netconf').as('getAllStatusNetconf')

    cy.visit('/')
    cy.contains('UniConfig').click()

    //20200514
    //this works on slower networks but not locally
    //when running fm on localhost then these xhrs are too fast to catch
    //wait a second for finishing of loading of the list of connected devices
    //there is two xhr we will wait for and after then 3 times bunch of xhrs
    //cy.wait(['@getAllStatusCli', '@getAllStatusNetconf']).then((xhrs) => {
    //  const cliDev = xhrs[0].responseBody.topology[0].node
    //  const netconfDev = xhrs[1].responseBody.topology[0].node
    //  const rowCount = ((cliDev === undefined) ? 0 : cliDev.length) + ((netconfDev === undefined) ? 0 : netconfDev.length)
    //  cy.get('table tbody tr td:first-child', {timeout:5000}).should('have.length', rowCount)
    //})
    cy.waitForXHR('@getAllStatusCli', '@getAllStatusNetconf')
    //REPLACE WITH SOMETHING LESS PRONE TO FAIL
    //cy.get('table tbody tr:nth-child(10)').should('to.exist')
    //cy.wait(100)

    cy.get('table tbody tr td:first-child div input').click({multiple:true})

    cy.contains('Unmount Devices').click()
    cy.get('table tbody tr').should('not.to.exist')
  })
})
