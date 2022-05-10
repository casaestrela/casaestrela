odoo.define('evo_pos_display_product_qty.CustomCasaProductScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
    const { useState } = owl.hooks;
    const { parse } = require('web.field_utils');
    const { Gui } = require('point_of_sale.Gui');
    
    const MyProductScreen = (ProductScreen) =>
    	class extends ProductScreen {
    	
    	
    }
    Registries.Component.extend(ProductScreen, MyProductScreen);
    return MyProductScreen;
    
//    const CustomCasaProductScreen = (ProductScreen) =>
//    class extends ProductScreen {
 	   
//    	_onClickPay() {
//        	var core = require('web.core');
//            var _t = core._t;
//            var order = this.env.pos.get_order();
//            var lines = order.get_orderlines();
//            if(this.env.pos.config.restric_product_sale === true) 
//            {
//	            if(lines.length > 0)
//	    		{
//		            for(var i=0; i<lines.length; i++)
//		            {
//	            		if(lines[i].product.stock_location_qty <  lines[i].quantity)
//		            	{
//		            		this.showPopup('ErrorPopup', {
//				                title: this.env._t('Product'),
//				                body: this.env._t(lines[i].product.display_name +' have no more than '+lines[i].product.stock_location_qty+' quantity'),
//				            });
//		            		break;
//		            	}
//	            		else
//	            		{
//	            			this.showScreen('PaymentScreen');
//	            		}
//		            }
//	    		}
//	            else
//	            {
//	            	this.showScreen('PaymentScreen');
//	            }
//            }
//            else
//            {
//            	this.showScreen('PaymentScreen');
//            }
//            
//        }
//    	
//    	async _clickProduct(event) {
//        	var core = require('web.core');
//            var _t = core._t;
//            var order = this.env.pos.get_order();
//            var lines = order.get_orderlines();
//            if(this.env.pos.config.restric_product_sale === true) 
//            {
//	            if(event.detail.stock_location_qty <= 0) 
//	            {
//		            this.showPopup('ErrorPopup', {
//		                title: this.env._t('Product'),
//		                body: this.env._t('This Product have no quantity'),
//		            });
//	            }
//	            else
//	            {
//		            if (!this.currentOrder) {
//		                this.env.pos.add_new_order();
//		            }
//		            const product = event.detail;
//		            const options = await this._getAddProductOptions(product);
//		            // Do not add product if options is undefined.
//		            if (!options) return;
//		            // Add the product after having the extra information.ntOrder.orderlines,this.currentOrder.orderlines._byId)
//		            if(lines.length > 0)
//            		{
//			            for(var i=0; i<lines.length; i++)
//			            {
//			            	
//			            	if(event.detail ==  lines[i].product)
//			            	{
//			            		if(event.detail.stock_location_qty <=  lines[i].quantity)
//				            	{
//				            		this.showPopup('ErrorPopup', {
//						                title: this.env._t('Product'),
//						                body: this.env._t('This Product have no more quantity'),
//						            });
//				            	}
//			            		if(event.detail.stock_location_qty >  lines[i].quantity)
//			            		{
//			            			this.currentOrder.add_product(product, options);
//			            		}
//			            	}
//			            	else
//			            	{	
//			            		this.currentOrder.add_product(product, options);
//			            	}
//			            }
//            		}
//		            else
//		            {
//		            	this.currentOrder.add_product(product, options);
//		            }
//		            
//		            NumberBuffer.reset();
//	            }
//            }
//            else
//            {
//            	if (!this.currentOrder) {
//	                this.env.pos.add_new_order();
//	            }
//	            const product = event.detail;
//	            const options = await this._getAddProductOptions(product);
//	            // Do not add product if options is undefined.
//	            if (!options) return;
//	            // Add the product after having the extra information.ntOrder.orderlines,this.currentOrder.orderlines._byId)
//	            this.currentOrder.add_product(product, options);
//	            NumberBuffer.reset();
//            }
//        }
//    }
//    Registries.Component.extend(ProductScreen, CustomCasaProductScreen);
//    return CustomCasaProductScreen;

});


