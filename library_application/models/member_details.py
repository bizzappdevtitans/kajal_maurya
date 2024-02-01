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
        comodel_name="book.loan.details",
        string="Book Loan",
        relation="member_bookloan_relation",
        column1="member_id",
        column2="bookloan_ids",
    )
    book_borrowed_count = fields.Integer(
        string="Book Borrowed Count", compute="_compute_book_borrowed_count"
    )
    sequence_no = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
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

    ## Sequence for member.details
    @api.model
    def create(self, vals):
        if vals.get("sequence_no", _("New")) == _("New"):
            vals["sequence_no"] = self.env["ir.sequence"].next_by_code(
                "member.details"
            ) or _("New")
        result = super(MemberDetails, self).create(vals)
        return result

    def write(self, vals):
        if "name" in vals:
            vals["name"] = vals["name"].capitalize()
        return super(MemberDetails, self).write(vals)

    def unlink(self):
        if self.bookloan_ids:
            raise UserError("You can't delete the record")
        return super(MemberDetails,self).unlink()

    def name_get(self):
        result = []
        for record in self:
            result.append(
                    (record.id, "%s - %s" % (record.name, record.sequence_no))
                )
        return result


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name :
            args += ['|',('name', operator, name), ('email', operator, name),]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)




