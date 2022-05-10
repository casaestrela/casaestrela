odoo.define('evo_msp_enhancement.msp_allow', function(require) {'use strict';
const { Gui } = require('point_of_sale.Gui');
const PosComponent = require('point_of_sale.PosComponent');
const { posbus } = require('point_of_sale.utils');
const ProductScreen = require('point_of_sale.ProductScreen');
const { useListener } = require('web.custom_hooks');
const Registries = require('point_of_sale.Registries');
const PaymentScreen = require('point_of_sale.PaymentScreen');
const ajax = require('web.ajax');

class MSPAllow extends PosComponent {
    constructor() {
        super(...arguments);
        useListener('click', this.onClick); 
    }
    get get_highlight()
    {
    	var order = this.env.pos.get_order();
    	if(order.get_allow_msp() === true)
    	{
    		return true
    	}
    	else
    	{
    		return false
    	}
    	
    	
    }
    onClick() {
    	var order = this.env.pos.get_order();
    	if(order.get_allow_msp() === true)
    	{
    		var order = this.env.pos.get_order();
    		order.set_allow_msp(false);
    	    this.get_highlight;
    	    this.env.pos.load_server_data();
    	}
    	else
    	{
    		var order = this.env.pos.get_order();
    		order.set_allow_msp(true);
    		this.get_highlight;
    		this.env.pos.load_server_data();
    	}
    }
}
MSPAllow.template = 'MSPAllow';
ProductScreen.addControlButton({
    component: MSPAllow,
    condition: function() {
        return this.env.pos;
    },
});
Registries.Component.add(MSPAllow);
return MSPAllow;


});