// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
require('@4tw/cypress-drag-drop')

Cypress.Commands.add("unmount_all_devices", () => {
    cy.visit('/') 
    cy.contains('UniConfig').click()	  
    //cy.contains('Refresh').click()
    //cy.get('table tbody tr td:first-child',{timeout:"10000"}).click({multiple:true})
    //cy.contains('connected').parent().find('td').eq(0).click()
    //cy.contains('connected').parent().find('td').eq(0).click()
    cy.wait(1000)
    cy.get('table tbody tr td:first-child').click({multiple:true})
    cy.contains('Unmount Devices').click()	  
    cy.get('table tbody tr').should('not.to.exist')
})

Cypress.Commands.add("unmount_incompatible_devices", () => {
    //Make sure you didn’t skip mounting all devices in inventory, otherwise this workflow might not work correctly.
    //
    //This use case does not work with VRP01 and netconf-testtool devices. 
    cy.visit('/') 
    cy.contains('UniConfig').click()	  
    cy.contains('VRP01').parent().find('td').eq(0).click()
    cy.contains('Unmount Devices').click()	  
    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('Unmount Devices').click()	  
    cy.contains('VRP01').should('not.to.exist')
    cy.contains('netconf-testtool').should('not.to.exist')
})

if (!Cypress.env("SKIP_LOGIN")) {
Cypress.Commands.add("login", () => {
    cy.server({
      method: 'POST',
    })
    cy.route('/identitytoolkit/v3/relyingparty/verifyPassword?key=AIzaSyBjf7igOYiFFASYpYiNZgWQOPb96Epn1_A').as('getId')
    let login = Cypress.env('login')
    let password= Cypress.env('password')
    cy.visit('/login') 
    cy.get('input[type="email"]').click().type(login)
    cy.get('input[type="password"]').click().type(password, { log: false })
    cy.get('button').contains('Sign In').click()
    cy.wait('@getId',{timeout:30000})
    cy.contains('Workflows')
})
} else {
Cypress.Commands.add("login", () => {
;
})
}

//this is helper functions to solve very fast xhr on localhost FM server which I am unable to catch
//and at the same time function to wait for xhr ending on slower connections
//definition of the function is dependant on the value of CYPRESS_baseUrl=http://10.19.0.5:3000
//if (!Cypress.env("baseUrl").includes("localhost")) {
//if (false) {
if (!Cypress.env("baseUrl")=="http://localhost:3000") {
Cypress.Commands.add("waitForXHR", () => {
    cy.server()
    cy.route('/api/odl/oper/all/status/cli').as('getAllStatusCli')
    cy.route('/api/odl/oper/all/status//topology-netconf').as('getAllStatusNetconf')
    //20200514
    //THIS WORKS ON SLOWER NETWORKS BUT NOT LOCALLY
    //WHEN RUNNING FM ON localhost THEN THESE XHRs ARE TOO FAST TO CATCH
    //wait a second for finishing of loading of the list of connected devices
    //there is two xhr we will wait for and after then 3 times bunch of xhrs
    cy.wait(['@getAllStatusCli', '@getAllStatusNetconf']).then((xhrs) => {
      const cliDev = xhrs[0].responseBody.topology[0].node
      const netconfDev = xhrs[1].responseBody.topology[0].node
      const rowCount = ((cliDev === undefined) ? 0 : cliDev.length) + ((netconfDev === undefined) ? 0 : netconfDev.length)
      cy.get('table tbody tr td:first-child', {timeout:5000}).should('have.length', rowCount)
    })
})
} else {
Cypress.Commands.add("waitForXHR", () => {
;
})
}
