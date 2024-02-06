from odoo import models, fields,api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fine_amount_param = fields.Float(string="Fine Amount", config_parameter="fine_amount_param")



