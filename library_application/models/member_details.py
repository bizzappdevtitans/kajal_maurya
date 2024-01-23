from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MemberDetails(models.Model):
    _name = "member.details"
    _description = "Member Information"
    _inherit="mail.thread"
    name = fields.Char(string="Name")
    address = fields.Text(string="Address")
    email = fields.Char(string="Email")
    library_id = fields.Many2one("library.details", string="Library")
    membership_start_date = fields.Date(string="Membership_Start_Date")
    subscription_expiry_date = fields.Date(string="Subscription Expiry Date")
    subscription_status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        "Subscription Status",
    )
    bookloan_ids = fields.One2many("book.loan.details", "member_id", string="Book Loan")

    book_borrowed_count = fields.Integer(
        string="Book Borrowed Count", compute="_compute_book_borrowed_count"
    )

    @api.depends("bookloan_ids")
    def _compute_book_borrowed_count(self):
        for record in self:
            record.book_borrowed_count = len(record.bookloan_ids)

    @api.constrains("book_borrowed_count")
    def _check_total_book_borrowed(self):
        if self.book_borrowed_count < 0:
            raise ValidationError(_("Borrowed Book Count can't be negative"))
