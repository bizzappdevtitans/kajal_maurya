from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LibraryDetails(models.Model):
    _name = "library.details"
    _description = "Library Information"

    name = fields.Char(string="Name", required=True)
    address = fields.Text(string="Address")
    librarian = fields.Char(string="Librarian")
    founded_year = fields.Date(string="Founded year")
    email = fields.Char(string="Email")
    opening_hours = fields.Char(string="Opening Hours")
    total_books = fields.Integer(string="Total Books", compute="_compute_total_books")
    member_count = fields.Integer(
        string="Member Count", compute="_compute_member_count"
    )
    subscription_fee = fields.Float(string="Subscription Fee")
    book_ids = fields.One2many(comodel_name="book.details", inverse_name="library_id", string="Books")
    member_ids = fields.One2many(comodel_name="member.details", inverse_name="library_id", string="Member")
    bookloan_ids = fields.One2many(comodel_name="book.loan.details", inverse_name="library_id", string="Book Loan")
    members_count = fields.Integer(compute="_compute_members_count")

    # method for computing total books

    @api.depends("book_ids")
    def _compute_total_books(self):
        for record in self:
            record.total_books = len(record.book_ids)

    # method for computing total members

    @api.depends("member_ids")
    def _compute_member_count(self):
        for record in self:
            record.member_count = len(record.member_ids)

    # validation for 'total_books'

    @api.constrains("total_books")
    def _check_total_books(self):
        if self.total_books < 0:
            raise ValidationError(_("Total Books should not be negative"))

    # smart button implementation

    def _compute_members_count(self):
        for record in self:
            record.members_count = self.env["member.details"].search_count(
                [("library_id", "=", record.id)]
            )

    def count_members(self):
        if self.members_count == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Members",
                "view_mode": "form",
                "res_model": "member.details",
                "target": "current",
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
