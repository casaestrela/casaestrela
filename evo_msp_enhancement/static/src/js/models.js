odoo.define('evo_msp_enhancement.models', function(require) { 
   'use strict'; 
   
   const models = require('point_of_sale.models'); 
   var _super_posmodel = models.PosModel.prototype;
   var cust_models = require('point_of_sale.models');
   var _super_Order = models.Order.prototype;
   
   models.Order = models.Order.extend({
	      initialize: function (attributes, options) {
	          var res = _super_Order.initialize.apply(this, arguments);
	          this.set({
	              rounding: true,
	          });
	          this.allow_msp = true;
	          this.cheque_date;
	          this.cheque_number;
	          return this;
	      },
	      set_allow_msp: function (allow_msp) {
	    	  this.allow_msp = allow_msp;
	          this.trigger('change',this);
	      },
	      get_allow_msp: function () {
	    	  return this.allow_msp;
	      },
	      set_cheque_number: function (cheque_number) {
	    	  this.cheque_number = cheque_number;
	          this.trigger('change',this);
	      },
	      set_cheque_date: function (cheque_date) {
	      	  this.cheque_date = cheque_date;
	            this.trigger('change',this);
	        },
	      get_cheque_date: function () {
	    	  return this.cheque_date;
	      },
	      get_cheque_number: function () {
	      	  return this.cheque_number;
	        },
	      export_as_JSON: function () {
	          var orders = _super_Order.export_as_JSON.call(this);
	          orders.allow_msp = this.get_allow_msp() || false;
	          orders.cheque_number = this.get_cheque_number() || false;
	          orders.cheque_date = this.get_cheque_date() || false;
	          return orders;
	      },
	      export_for_printing: function () {
	          var orders = _super_Order.export_for_printing.call(this);
	          orders.allow_msp = this.get_allow_msp() || false;
	          orders.cheque_number = this.get_cheque_number() || false;
	          orders.cheque_date = this.get_cheque_date() || false;
	          return orders;
	      },
   });
   
});