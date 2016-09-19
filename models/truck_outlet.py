from openerp import api, fields, models


class TruckOutlet(models.Model):
    _inherit = ['truck', 'vehicle.outlet', 'mail.thread']
    _name = 'truck.outlet'

    state = fields.Selection([
        ('analysis', 'Analysis'),
        ('weight_input', 'Weight Input'),
        ('unloading', 'Unloading'),
        ('weight_output', 'Weight Output'),
        ('done', 'Done'),
    ], default='analysis')

    _defaults = {'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'reg_code'), }

    @api.one
    @api.depends('contract_id', 'clean_kilos')
    def _compute_delivered(self):
        self.delivered = sum(record.clean_kilos for record in self.contract_id.truck_outlet_ids) / 1000

    @api.one
    def fun_unload(self):
        self.state = 'weight_output'

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'analysis':
                self.write({'state': 'weight_input'}, 'r')
            elif self.state == 'weight_input':
                self.write({'state': 'unloading'}, 'r')
            elif self.state == 'unloading':
                self.write({'state': 'weight_output'}, 'r')
            elif self.state == 'weight_output':
                self.write({'state': 'done'}, 'r')

        res = super(TruckOutlet, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        vals['state'] = 'weight_input'
        res = super(TruckOutlet, self).create(vals)
        return res
