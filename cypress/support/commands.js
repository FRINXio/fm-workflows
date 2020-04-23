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
    cy.contains('netconf-testtool').parent().find('td').eq(0).click()
    cy.contains('Unmount Devices').click()	  
    cy.contains('VRP01').should('not.to.exist')
    cy.contains('netconf-testtool').should('not.to.exist')
})

if (!Cypress.env("SKIP_LOGIN")) {
Cypress.Commands.add("login", () => {
    let login = Cypress.env('login')
    let password= Cypress.env('password')
    cy.visit('/login') 
    cy.get('input[type="email"]').click().type(login)
    cy.get('input[type="password"]').click().type(password, { log: false })
    cy.get('button').contains('Sign In').click()
    cy.contains('Workflows')
})
} else {
Cypress.Commands.add("login", () => {
;
})
}
