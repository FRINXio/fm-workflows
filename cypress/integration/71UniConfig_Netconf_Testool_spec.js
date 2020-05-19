describe('Mount devices from UniConfig', function() {
  beforeEach(function() {
    cy.login()
  })

  it('Mount netconf device netconf-testtool', function() {
    var device_id='netconf-testtool'
    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfig')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfigO')

    cy.visit('/')
    cy.contains('UniConfig').click()
    cy.url().should('include', '/devices')

    cy.contains('Mount Device').click()

    cy.contains('Netconf').click()
    // this does not work - why ??? cy.contains('Basic').click()
    //cy.get('div.tab-content').contains('Basic', {force:true}).click()// nefunguje lebo najde prvy Basic na prvom paneli ktory je hidden
    cy.get('#mountTabs-tabpane-Netconf').contains('Basic').click()

    cy.get('#mountnetconfInput-node-id')
      .clear()
      .type(device_id)
      .should('have.value', device_id)

    cy.get('#mountnetconfInput-host')
      .clear()
      .type('sample-topology')
      .should('have.value', 'sample-topology')

    cy.get('#mountnetconfInput-port')
      .clear()
      .type('1783')
      .should('have.value', '1783')

    cy.get('#mountnetconfInput-username')
      .clear()
      .type('cisco')
      .should('have.value', 'cisco')

    cy.get('#mountnetconfInput-password')
      .clear()
      .type('cisco')

    cy.get('#mountTabs-tabpane-Netconf').contains('Advanced').click()
    cy.contains('UniConfig Native').click()
    cy.contains('Blacklist').parent().find(':checkbox').click()

    cy.get('button[class="btn btn-primary"]').contains('Mount Device')
      .then(($button) => {
      $button.click()
      })

    cy.get('button[class="btn btn-primary"]').should('not.to.exist')
    cy.get('button.btn.btn-success', { timeout : 30000  } ).should('contain','Connected')
    cy.contains('Close').click()
    cy.get('div.modal-dialog.modal-lg').should('not.to.exist')

    //cy.get('table tbody tr').should('have.length',2)
    cy.get('table tbody tr').should('to.exist')

    //20200518THIS WORKED IN V1.1 BUT STOPPED TO WORK IN V1.2 DUE TO CHANGE OF CLASS (ALIGN CENTER-> ALIGN LEFT)
    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    //20200518 wait only for the second xhr
    cy.wait('@getConfigO',{timeout:30000})
    cy.url().should('include', '/devices/edit/' + device_id)

    cy.get('button[class~="round"]').click({force:true})
    cy.contains('Refresh').click()
  })

  it('Configure - testing of controls  - netconf-testtool', function()  {
    var device_id='netconf-testtool'
/*  it('Configure - testing of controls  - ' + device_id, (done) =>  {

  cy.on('uncaught:exception', (err, runnable) => {
    expect(err.message).to.include('something about the error')

    // using mocha's async done callback to finish
    // this test so we prove that an uncaught exception
    // was thrown
    //done()

    // return false to prevent the error from
    // failing this test
    return false
  })
*/
    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfig')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfigO')
    cy.server({
      method: 'POST',
    })
    cy.route('/api/odl/operations/sync-from-network').as('getConfigFromNetwork')
    cy.route('/api/odl/operations/replace-config-with-operational').as('getConfigFromOperational')
    cy.route('/api/odl/operations/create-snapshot').as('postCreateSnapshot')

    cy.visit('/')
    cy.contains('UniConfig').click()

    cy.url().should('include', '/devices')

    //20200518THIS WORKED IN V1.1 BUT STOPPED TO WORK IN V1.2 DUE TO CHANGE OF CLASS (ALIGN CENTER-> ALIGN LEFT)
    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    //20200518 wait only for the second xhr
    cy.wait('@getConfigO')
    cy.url().should('include', '/devices/edit/' + device_id)

    //******************
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Console output of')
    cy.contains('{}')
    cy.contains('Close').click()

    //Sync from network (refresh actual configuration window)
    cy.contains('Sync from network').click()
    cy.wait('@getConfigFromNetwork')
    cy.wait('@getConfig')
    //close alert
    cy.get('.options ~ div[role="alert"]').contains('SYNC-FROM-NETWORK :')
    cy.get('.options ~ div[role="alert"]').contains('Node-status: complete')
    cy.get('.options ~ div[role="alert"] > i').click()
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Console output of Sync-from-network')
    cy.contains('Close').click()

    //Save Intended Configuration (after change)
    cy.contains('Save').click()
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Close').click()

    //Refresh (refresh intended configuration window)
    cy.contains('Refresh').click()
    cy.wait('@getConfig')
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Close').click()

    //Refresh/Replace with Operational
    cy.contains('Refresh').next().click()
    cy.contains('Replace with Operational').click()
    cy.wait('@getConfigFromOperational')
    cy.wait('@getConfig')
    //close alert
    cy.get('.options ~ div[role="alert"]').contains('REPLACE-CONFIG-WITH-OPERATIONAL:')
    cy.get('.options ~ div[role="alert"]').contains('Node-status: complete')
    cy.get('.options ~ div[role="alert"] > i').click()
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Console output of Replace-config-with-operational')
    cy.contains('Close').click()

    //Create snapshot
    var Idx='_001'
    cy.contains('Create snapshot').click()
    cy.get('#snapshotNameInput').clear().type(device_id + Idx).should('have.value', device_id + Idx)
    cy.contains('Save Snapshot').click()
    cy.wait('@postCreateSnapshot')
    cy.contains('Close').click()
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Close').click()

    //Load snapshot
    cy.contains('Load Snapshot').click()
    cy.contains(device_id + Idx).click()
    //close alert
    cy.get('.options ~ div[role="alert"]').contains('REPLACE-CONFIG-WITH-SNAPSHOT:')
    cy.get('.options ~ div[role="alert"]').contains('Node-status: complete')
    cy.get('.options ~ div[role="alert"] > i').click()
    //Display console
    cy.get('span#consoleButton').click()
    cy.contains('Console output of Replace-Config-With-Snapshot')
    cy.contains('Close').click()

    // TODO Toggle deleting

    //Show Diff
    cy.contains('Show Diff').click()
    cy.screenshot() 
    //here in FM v1.1. there is a bug
    //after loading snapshot there is native-529687306-Cisco-IOS-XR-ifmgr-cfg:interface-configurations clause in Intended Configuration
    //which is the reason for unexpected difference
    cy.get('div.operational div.d2h-file-header').contains('Operational CHANGED')
    cy.get('div.operational div.d2h-file-diff').contains('File without changes')
    //example:
    //cy.get('@OutputBox').should(($json) => {
    //  expect($json, 'to expect to find in OUTPUT box of CLI_execute_and_read_rpc_cli (COMPLETED) workflow:').to.contain('interface Loopback')
    //  expect($json, 'to expect to find in OUTPUT box of CLI_execute_and_read_rpc_cli (COMPLETED) workflow:').to.contain('interface GigabitEthernet')
    //})
    
    //Hide diff
    cy.contains('Hide Diff').click()
    cy.contains('Show Diff').next().click()
    cy.contains('Get calculated diff').click()

    cy.get('span#consoleButton').click()
    cy.contains('Console output of Calculated Diff')
    cy.contains('Close').click()

    cy.contains('Dry run').click()

    cy.get('.options ~ div[role="alert"]').contains('DRY-RUN FAIL')
    cy.get('.options ~ div[role="alert"]').contains('Node does not support dry-run')
    cy.get('.options ~ div[role="alert"] > i').click()

    cy.contains('Commit to network').click()

    cy.get('.options ~ div[role="alert"]').contains('COMMIT-TO-NETWORK')
    cy.get('.options ~ div[role="alert"]').contains('Node-status: complete')
    cy.get('.options ~ div[role="alert"] > i').click()

    cy.get('span#consoleButton').click()
    cy.contains('Console output of Commit to Network')
    cy.contains('Close').click()

    cy.get('div.operational > div > div > div.ReactCodeMirror > textarea').contains(': "192.168.1.213",')
    cy.get('div.config > div > div > div.ReactCodeMirror > textarea').contains(': "192.168.1.213",')
    //cy.get('div.operational').find('pre.CodeMirror-line span span').contains('192.168.1.213')

    //******************
    //Leave devices/edit page
    cy.get('button[class~="round"]').click({force:true})
    //20200518 wait only for the second xhr
    cy.wait('@getConfigO')
    cy.url().should('include', '/devices')
  })
})
