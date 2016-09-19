from openerp import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    truck_outlet_ids = fields.One2many('truck.outlet', 'contract_id')

    def truck_outlet(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        dummy, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'truck_outlet', 'truck_outlet_list_action'))
        action = self.pool.get('ir.actions.act_window').read(cr, uid, action_id, context=context)
        res = mod_obj.get_object_reference(cr, uid, 'truck_outlet', 'truck_outlet_form_view')
        action['views'] = [(res and res[1] or False, 'form')]
        action['context'] = {'default_contract_id': ids[0]}
        return action
