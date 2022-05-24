odoo.define('evo_pos_msp.models', function(require) { 
   'use strict'; 
   
   const models = require('point_of_sale.models'); 
   var _super_Orderline = models.Orderline.prototype;
   
   models.Orderline = models.Orderline.extend({
	   
	   initialize: function(attr,options){
		   var res = _super_Orderline.initialize.apply(this, arguments);
		   this.msp_percentage = 0;
		   this.msp_subtotal = 0;
		   return this;
	   },
	   get_msp_per: function () {
	    	  var msp_per =  this.product.msp_percentage;
	    	  return msp_per;
	      },
	   export_as_JSON: function() {
		   var ordersline = _super_Orderline.export_as_JSON.call(this);
		   ordersline.msp_percentage = this.get_msp_per() || false;
	       return ordersline;
	   },
	   export_for_printing: function(){
		   var ordersline = _super_Orderline.export_for_printing.call(this);
		   ordersline.msp_percentage = this.get_msp_per() || false;
	       return ordersline;
	   },
   });
});