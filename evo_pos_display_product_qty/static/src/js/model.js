odoo.define('evo_pos_display_product_qty.model', function (require) {
"use strict";

var module = require('point_of_sale.models');
var models = module.PosModel.prototype.models;

for(var i=0; i<models.length; i++)
{
    var model=models[i];
    if(model.model === 'product.product')
    {
         model.fields.push('stock_location_qty');
    } 
}

});