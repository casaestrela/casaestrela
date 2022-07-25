odoo.define('evo_pos_payment_enhancement.ChequeInformation', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useState, useRef, useContext} = owl.hooks;
    const contexts = require('point_of_sale.PosContext');
    const ajax = require('web.ajax');

    class ChequeInformation extends PosComponent {
    	
    	constructor() {
            super(...arguments);
            this.changes = {
                error: null,
                cheque_number: '',
                cheque_date: null,
            }
            if (this.props.cheque_number) {
                this.changes['cheque_number'] = this.props.cheque_number
            }
            if (this.props.cheque_bank_id) {
                this.changes['cheque_date'] = this.props.cheque_date
            }
            this.state = useState(this.changes);
            this.orderUiState = useContext(contexts.orderManagement);
        }
    confirm() {
    		var self = this;
    		var order =  self.env.pos.get_order();
    		order.set_cheque_number(this.state.cheque_number);
    		order.set_cheque_date(this.state.cheque_date);
    		this.trigger('close-popup');
    	}
    	getPayload() {
            return this.changes
        }
    	cancel() {
    		this.trigger('close-popup');
        }
    }
    
    ChequeInformation.template = 'ChequeInformation';
    ChequeInformation.defaultProps = {
            confirmText: 'Ok',
            cancelText: 'Cancel',
            title: '',
            body: '',
        };

     Registries.Component.add(ChequeInformation);

    return ChequeInformation;
});
