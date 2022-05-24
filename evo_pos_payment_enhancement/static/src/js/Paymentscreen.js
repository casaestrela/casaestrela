odoo.define('evo_pos_payment_enhancement.Paymentscreen', function(require) { 
   'use strict'; 
   
   const PaymentScreen = require('point_of_sale.PaymentScreen');
   const Registries = require('point_of_sale.Registries');
   const ajax = require('web.ajax');
   const NumberBuffer = require('point_of_sale.NumberBuffer');
   

   const CustomPaymentScreen = (PaymentScreen) =>
   class extends PaymentScreen {
	   
	   async validateOrder(isForceValidate) {
		   if(!this.currentOrder.get_client())
		   {
			   const { confirmed } = await this.showPopup('ConfirmPopup', {
                   title: this.env._t('Please select the Customer'),
                   body: this.env._t(
                       'You need to select the customer before you can invoice an order.'
                   ),
               });
               if (confirmed) {
                   this.selectClient();
               }
               return false;
		   }
           if(this.currentOrder.is_to_invoice())
           {
           		await this._finalizeValidation();
           }
       }
	   async setChequeInformation(event) {
           
		   let { confirmed, payload: datas } = await this.showPopup('ChequeInformation', {
               
               title: this.env._t('Add Cheque Information'),
           });
           return true;
	   }
	   
	   addNewPaymentLine({ detail: paymentMethod }) {
           // original function: click_paymentmethods
   		if(paymentMethod)
   		{
   			if(paymentMethod.is_cheque === true)
   	   		{
   				this.currentOrder.add_paymentline(paymentMethod);
   	   			this.setChequeInformation({detail:paymentMethod});
   	   		}
   	   		else 
   	   		{
   	   			if (this.currentOrder.electronic_payment_in_progress()) {
   	                this.showPopup('ErrorPopup', {
   	                    title: this.env._t('Error'),
   	                    body: this.env._t('There is already an electronic payment in progress.'),
   	                });
   	                return false;
   	            } else {
   	                this.currentOrder.add_paymentline(paymentMethod);
   	                NumberBuffer.reset();
   	                this.payment_interface = paymentMethod.payment_terminal;
   	                if (this.payment_interface) {
   	                    this.currentOrder.selected_paymentline.set_payment_status('pending');
   	                }
   	                return true;
   	            }
   	   		}
   		}
   		
           
       }
	   
   }
	Registries.Component.extend(PaymentScreen, CustomPaymentScreen);
	return CustomPaymentScreen;
   
});