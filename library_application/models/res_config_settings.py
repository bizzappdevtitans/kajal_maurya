from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    max_book_per_user = fields.Integer(
        string="Max Book", config_parameter="max_book_per_user"
    )
    book_return_period = fields.Integer(
        string="Book Return Period", config_parameter="book_return_period"
    )


