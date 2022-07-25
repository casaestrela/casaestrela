odoo.define('evo_pos_payment_enhancement.model', function (require) {
"use strict";

var module = require('point_of_sale.models');
var models = module.PosModel.prototype.models;
for(var i=0; i<models.length; i++)
{
    var model=models[i];
    if(model.model === 'pos.payment.method')
    {
         model.fields.push('is_cheque');
    } 
    if(model.model === 'pos.payment')
    {
         model.fields.push('cheque_number');
    } 
    if(model.model === 'pos.payment')
    {
         model.fields.push('cheque_date');
    } 
}

});