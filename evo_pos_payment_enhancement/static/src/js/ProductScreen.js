odoo.define('evo_pos_payment_enhancement.CustomProductScreen', function(require) { 
   'use strict'; 
   
   const ProductScreen = require('point_of_sale.ProductScreen');
   const Registries = require('point_of_sale.Registries');
   const {posbus} = require('point_of_sale.utils');
   const NumberBuffer = require('point_of_sale.NumberBuffer');
   var BarcodeEvents = require('barcodes.BarcodeEvents').BarcodeEvents;
   const {useListener} = require('web.custom_hooks');
   const {useState} = owl.hooks;
   
//   const CustomProductScreen = (ProductScreen) =>
//   class extends ProductScreen {
//	   
//	   _onClickPay() {
//		   var selectedOrder = this.env.pos.get_order();
//		   var lines = selectedOrder.get_orderlines();
//		   var core = require('web.core');
//           var _t = core._t;
//	       if(lines.length > 0)
//	       {
//		       for(var i=0; i<lines.length; i++)
//		       {
//		    	   var order_price = lines[i].price
//		    	   var pricelist_price = lines[i].get_product().get_price(lines[i].order.pricelist, lines[i].quantity)
//		    	   if(pricelist_price > order_price)
//		    	   {
//		    		   this.showPopup('ErrorPopup', {
//			                title: this.env._t('Price'),
//			                body: this.env._t('Price cannot be lower then price list'),
//			            });
//	            		break;
//	            		this.showScreen('ProductScreen');
//		    	   }
//		    	   else
//		    	   {
//		    		   
//		    			   this.currentOrder.set_to_invoice(true);
//			   		   		this.showScreen('PaymentScreen');
//		    		   	
//		    	   }
//		       }
//	       }
//		    
//	   }
//   }
//   Registries.Component.extend(ProductScreen, CustomProductScreen);
//   return CustomProductScreen;
   
});