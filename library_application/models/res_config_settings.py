from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    fine_amount = fields.Integer(string="Fine Amount", config_parameter="fine_amount")

