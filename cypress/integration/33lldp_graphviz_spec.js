//https://docs.frinx.io/frinx-machine/use-cases/lldp-topology/lldp-topology.html
//Obtain LLDP topology data
//Collect LLDP Information from Devices and Build Topology
describe('Collect LLDP Information from Devices and Build Topology', function() {
  it.skip('goes to 3rd party visualization tool', function() {
    //Finally you can use any 3rd party visualization tool that can support the graphviz format like https://dreampuf.github.io/GraphvizOnline.
    cy.visit('https://dreampuf.github.io/GraphvizOnline')
    cy.wait(1000)
    cy.readFile('cypress/fixtures/lldp_export.json').then((json) => {
      expect(json).to.be.an('object')

      cy.get('textarea.ace_text-input').clear({force:true})
      cy.get('textarea.ace_text-input').invoke('show').type('{selectall}{backspace}',{force:true})
      cy.get('textarea.ace_text-input').invoke('show').type('{selectall}{del}',{force:true})

      console.log(json.export.output.export)
	    
      //https://github.com/cypress-io/cypress/issues/1123
      cy.get('textarea.ace_text-input').invoke('show').type(json.export.output.export.replace(/\\n/g, ''),{force:true, delay: 0})

      // I tried hard but nothing work only that above
      //const myValue = json.export.output.export.replace(/\\n/g, '')
      //console.log(myValue)
      //cy.get('textarea.ace_text-input').then($span => {
      //      $span.val('really long text');
      //});	   
      //cy.get('textarea.ace_text-input').clear({force:true}).trigger('blur',{force:true})
      //cy.get('textarea.ace_text-input').invoke('val', myValue).trigger('change',{force:true})
      //Cypress.$('textarea.ace_text-input').val(json.export.output.export).keypress()
      //cy.get('textarea').invoke('val', myValue').trigger('change')
    })
  })
})
