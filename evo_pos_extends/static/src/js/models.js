odoo.define('evo_pos_extends.models', function (require) {
"use strict";

var module = require('point_of_sale.models');
var models = module.PosModel.prototype.models;
for(var i=0; i<models.length; i++)
{
    var model=models[i];
    if(model.model === 'res.partner')
    {
         model.fields.push('operating_unit_ids','user_id');
    } 
    if(model.model === 'res.users')
    {
         model.fields.push('operating_unit_ids');
    } 
}
});