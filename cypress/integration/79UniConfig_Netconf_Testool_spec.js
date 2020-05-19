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

    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    cy.wait('@getConfig',{timeout:30000})
    cy.url().should('include', '/devices/edit/' + device_id)

    cy.get('button[class~="round"]').click({force:true})
    cy.contains('Refresh').click()
  })

  it('TEST2 netconf-testtool', function() {
    var device_id='netconf-testtool'
    cy.server({
      method: 'GET',
    })
    cy.route('/api/odl/conf/uniconfig/' + device_id).as('getConfig')
    cy.route('/api/odl/oper/uniconfig/' + device_id).as('getConfig')
    cy.server({
      method: 'POST',
    })
    cy.route('/api/odl/operations/sync-from-network').as('getConfigFromNetwork')
    cy.route('/api/odl/operations/replace-config-with-operational').as('getConfigFromOperational')
    cy.route('/api/odl/operations/create-snapshot').as('postCreateSnapshot')

    cy.visit('/')
    cy.contains('UniConfig').click()

    cy.url().should('include', '/devices')

    cy.contains(device_id).parent().find('td').eq(5).find('button').click()
    cy.wait('@getConfig', {timeout:30000})
    cy.url().should('include', '/devices/edit/' + device_id)

    //******************
    //--> backup intended config
    //define element
    cy.get('div.config > div > div > div.ReactCodeMirror > textarea').as('intended_conf')
    //write content to file
    cy.get('@intended_conf').then(($code) => {
      const txt = $code.text() 
      console.log(txt)
      const d = new Date();
      const localtime = d.toLocaleTimeString('en-US', { hour12: false }).split(':').join('');
      cy.writeFile('cypress/fixtures/intendedConf' +  localtime +  '.json', txt)
    })

    const d = new Date();
    const localtime = d.toLocaleTimeString('en-US', { hour12: false }).split(':').join('');

    //Create snapshot
    var Idx='_001' + localtime
    cy.contains('Create snapshot').click()
    cy.get('#snapshotNameInput').clear().type(device_id + Idx).should('have.value', device_id + Idx)
    cy.contains('Save Snapshot').click()
    cy.wait('@postCreateSnapshot')
    cy.contains('Close').click()
/*
    //--> Intended configuration - add loopback block
    //https://stackoverflow.com/questions/55362875/how-to-type-using-cypress-type-inside-the-codemirror-editor/55363197#55363197
    cy.get('.config .CodeMirror textarea').as('edit_conf')
    cy.get('@edit_conf').type('{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}{downarrow}',{force: true})
    cy.get('@edit_conf').type('{{}{enter}"active":"act",{enter}"interface-name":"loopback1000",{enter}"shutdown":[null]{enter}},{enter}',{force: true})
    //--> Expect
    cy.get('div.config div.d2h-file-header').contains('ODL config data store of netconf-testtool')
    cy.get('div.config div.d2h-file-header').contains('MODIFIED')

    //--> save
    //Save Intended Configuration (after change)
    cy.contains('Save').click()
    //--> Expect
    cy.get('div.config div.d2h-file-header').contains('ODL config data store of netconf-testtool')
    //cy.get('div.config div.d2h-file-header').should('not.contain','MODIFIED')
    //--> Display console
    cy.get('span#consoleButton').click()
    cy.contains('Console output of Update Config')
    cy.contains('"method": "PUT",')
    //cy.contains('"method": "url": "uniconfig:8181/rests/data/network-topology:network-topology/topology=uniconfig/node=netconf-testtool/frinx-uniconfig-topology:configuration",')
    cy.contains('Close').click()

    //Create snapshot
    var Idx='_002' + localtime
    cy.contains('Create snapshot').click()
    cy.get('#snapshotNameInput').clear().type(device_id + Idx).should('have.value', device_id + Idx)
    cy.contains('Save Snapshot').click()
    cy.wait('@postCreateSnapshot')
    cy.contains('Close').click()
*/
    //--> Show Diff
    cy.contains('Show Diff').click()
    //--> Hide diff
    cy.contains('Hide Diff').click()
    cy.contains('Commit to network').click()
    //--> Show Diff
    cy.contains('Show Diff').click()
    //--> Hide diff
    cy.contains('Hide Diff').click()
    cy.contains('Sync from network').click()
    //--> Show Diff
    cy.contains('Show Diff').click()
    //--> Hide diff
    cy.contains('Hide Diff').click()

    //Load snapshot
    cy.contains('Load Snapshot').click()
    cy.contains(device_id + Idx).click()

    cy.get('.options ~ div[role="alert"]').contains('REPLACE-CONFIG-WITH-SNAPSHOT:')
    cy.get('.options ~ div[role="alert"]').contains('Node-status: complete')
    cy.get('.options ~ div[role="alert"] > i').click()

    cy.get('span#consoleButton').click()
    cy.contains('Console output of Replace-Config-With-Snapshot')
    cy.contains('Close').click()
    //--> Show Diff
    cy.contains('Show Diff').click()
    cy.screenshot() 
    //--> Hide diff
    cy.contains('Hide Diff').click()

    // TEARDOWN TRY TO FIND LOOPBACK AND REMOVE THE CONFIG
    //--> backup intended config
    //write content to file
    cy.get('@intended_conf').then(($code) => {
      const txt = $code.text() 
      const d = new Date();
      const localtime = d.toLocaleTimeString('en-US', { hour12: false }).split(':').join('');
      cy.writeFile('cypress/fixtures/intendedConf' +  localtime +  '.json', txt)
    })
    cy.contains('Sync from network').click()
    cy.contains('Refresh').next().click()
    cy.contains('Replace with Operational').click()
    //--> Show Diff
    cy.contains('Show Diff').click()
    cy.screenshot() 
    //--> Hide diff
    cy.contains('Hide Diff').click()

    //--> backup intended config
    //write content to file
    cy.get('@intended_conf').then(($code) => {
      const txt = $code.text() 
      const d = new Date();
      const localtime = d.toLocaleTimeString('en-US', { hour12: false }).split(':').join('');
      cy.writeFile('cypress/fixtures/intendedConf' +  localtime +  '.json', txt)
    })

    //******************
    //Leave devices/edit page
    cy.get('button[class~="round"]').click({force:true})
    cy.url().should('include', '/devices')
  })
})
