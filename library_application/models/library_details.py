from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LibraryDetails(models.Model):
    _name = "library.details"
    _description = "Library Information"
    _order="sequence_handle"

    name = fields.Char(string="Name", required=True)
    address = fields.Text(string="Address")
    librarian = fields.Char(string="Librarian")
    founded_year = fields.Date(string="Founded year")
    email = fields.Char(string="Email")
    opening_hours = fields.Char(string="Opening Hours")
    total_books = fields.Integer(string="Total Books", compute="_compute_total_books")
    total_member_count = fields.Integer(
        string="Total Member Count", compute="_compute_total_member_count"
    )
    subscription_fee = fields.Float(string="Subscription Fee")
    book_ids = fields.One2many(
        comodel_name="book.details", inverse_name="library_id", string="Books"
    )
    member_ids = fields.One2many(
        comodel_name="member.details", inverse_name="library_id", string="Member"
    )
    bookloan_ids = fields.One2many(
        comodel_name="book.loan.details", inverse_name="library_id", string="Book Loan"
    )
    member_count = fields.Integer(compute="_compute_member_count")
    sequence_no = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    sequence_handle=fields.Integer(string="Sequence" ,default="1")


    # method for computing total books
    @api.depends("book_ids")
    def _compute_total_books(self):
        for record in self:
            record.total_books = len(record.book_ids)

    # method for computing total members
    @api.depends("member_ids")
    def _compute_total_member_count(self):
        for record in self:
            record.total_member_count = len(record.member_ids)

    # validation for 'total_books'
    @api.constrains("total_books")
    def _check_total_books(self):
        if self.total_books < 0:
            raise ValidationError(_("Total Books should not be negative"))

    def _compute_member_count(self):
        for record in self:
            record.member_count = self.env["member.details"].search_count(
                [("library_id", "=", record.id)]
            )

    # smart button implementation
    def action_count_members(self):
        if self.member_count == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Members",
                "view_mode": "form",
                "res_model": "member.details",
                "target": "new",
                "res_id": self.member_ids.id,
            }
        else:
            return {
                "type": "ir.actions.act_window",
                "name": "Members",
                "view_mode": "tree,form",
                "res_model": "member.details",
                "target": "current",
                "domain": [("library_id", "=", self.id)],
            }

    # Sequence for library.details
    @api.model
    def create(self, vals):
        if vals.get("sequence_no", _("New")) == _("New"):
            vals["sequence_no"] = self.env["ir.sequence"].next_by_code(
                "library.details"
            ) or _("New")
        result = super(LibraryDetails, self).create(vals)
        return result

    def write(self, vals):
        if "name" in vals:
            vals["name"] = vals["name"].capitalize()
        return super(LibraryDetails, self).write(vals)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s - %s" % (record.name, record.address)))
        return result

    @api.model
    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if name:
            args += [
                "|",
                ("name", operator, name),
                ("address", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(LibraryDetails, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )
