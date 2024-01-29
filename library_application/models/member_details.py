from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MemberDetails(models.Model):
    _name = "member.details"
    _description = "Member Information"

    name = fields.Char(string="Name")
    address = fields.Text(string="Address")
    email = fields.Char(string="Email")
    library_id = fields.Many2one(comodel_name="library.details", string="Library")
    membership_start_date = fields.Date(
        string="Membership Start Date", default=fields.Date.today()
    )
    subscription_expiry_date = fields.Date(
        string="Subscription Expiry Date", default=fields.Date.today()
    )
    subscription_status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
        ],
        string="Subscription Status",
        default="active",
        required=True,
    )
    bookloan_ids = fields.Many2many(
        comodel_name="book.loan.details", string="Book Loan"
    )
    book_borrowed_count = fields.Integer(
        string="Book Borrowed Count", compute="_compute_book_borrowed_count"
    )

    # method for computing borrowed book
    @api.depends("bookloan_ids")
    def _compute_book_borrowed_count(self):
        for record in self:
            record.book_borrowed_count = len(record.bookloan_ids)

    # validation for borrowed book
    @api.constrains("book_borrowed_count")
    def _check_total_book_borrowed(self):
        if self.book_borrowed_count < 0:
            raise ValidationError(_("Borrowed Book Count can't be negative"))

    # validation of 'membership_start_date' with 'subscription_expiry_date'
    @api.onchange("membership_start_date")
    def _onchange_membership_start_date(self):
        if self.membership_start_date > self.subscription_expiry_date:
            raise ValidationError(
                _(
                    "membership_start_date should not be greater than subscription_expiry_date"
                )
            )

    """method for changing the value of subscription_status on the basis of
    subscription_expiry_date"""

    @api.onchange("subscription_expiry_date")
    def _onchange_subscription_expiry_date(self):
        if self.subscription_expiry_date < fields.Date.today():
            self.subscription_status = "inactive"
        else:
            self.subscription_status = "active"
