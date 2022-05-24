odoo.define('evo_pos_extends.customer_filter_pos', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	var session = require('web.session');
	var _super_posmodel = models.PosModel.prototype;
	var ajax = require('web.ajax');
	
	models.load_models([
    {
 	   model: 'operating.unit',
 	   fields: ['id','name','code'],
 	   
 	   loaded: function(self,result)
 	   {
 		   self.operating_unit_id = result;
 	   },
    }],{'after': 'product.product'});
	
	models.PosModel = models.PosModel.extend({
        initialize: function (session,attributes) {
			var self = this;
			var unit_list = [];
			var res = _super_posmodel.initialize.call(this, session,attributes);
			var partner_model = _.find(this.models, function(model){
				
				return model.model === 'res.partner';
			});
			var result = ajax.jsonRpc('/get_operating_unit', 'call', {
                'user': session.session.uid,
                'async': true,
                
            }).then(function(response) {
            	partner_model['domain'] = [['operating_unit_ids', 'in', response]];
            });
            return res;
        },
    });
});



//models.PosModel = models.PosModel.extend({
//    initialize: function (session,attributes) {
//		var self = this;
//		var unit_list = [];
////		console.log('------session------------------',session,session.uid);
////		debugger;
//        var partner_model = _.find(this.models, function(model){
//        	ajax.jsonRpc('/get_operating_unit', 'call', {
//                'user': session.session.uid,
//                
//            }).then(function(response) {
//            	console.log('--------response-----------',response);
//            	self.unit_list = response;
//            });
//        	console.log('---11------unit_list--------------',self.unit_list)
//            return model.model === 'res.partner';
//            
//        });    
//        console.log('---------unit_list--------------',self.unit_list)
////		partner_model['domain'] = [['operating_unit_ids', '=', unit_list]];
////        var res = _super_posmodel.initialize.call(this, session,attributes);       
//        return _super_posmodel.initialize.call(this, session,attributes);
//    },
//});