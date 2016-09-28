from openerp import api, fields, models


class TruckOutlet(models.Model):
    _inherit = ['truck', 'vehicle.outlet', 'mail.thread']
    _name = 'truck.outlet'

    state = fields.Selection([
        ('analysis', 'Analysis'),
        ('weight_input', 'Weight Input'),
        ('loading', 'Loading'),
        ('weight_output', 'Weight Output'),
        ('done', 'Done'),
    ], default='analysis')

    _defaults = {'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'reg_code_to'), }

    @api.one
    @api.depends('contract_id')
    def _compute_product_id(self):
        product_id = False
        for line in self.contract_id.order_line:
            product_id = line.product_id.id
            break
        self.product_id = product_id

    @api.one
    @api.depends('input_kilos', 'output_kilos')
    def _compute_raw_kilos(self):
        self.raw_kilos = self.output_kilos -self.input_kilos

    @api.one
    @api.depends('contract_id', 'clean_kilos')
    def _compute_delivered(self):
        self.delivered = sum(record.clean_kilos for record in self.contract_id.truck_outlet_ids) / 1000

    @api.one
    def fun_load(self):
        self.state = 'weight_output'

    @api.multi
    def write(self, vals, recursive=None):
        if not recursive:
            if self.state == 'analysis':
                self.write({'state': 'weight_input'}, 'r')
            elif self.state == 'weight_input':
                self.write({'state': 'loading'}, 'r')
            elif self.state == 'loading':
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
