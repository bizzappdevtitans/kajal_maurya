from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BookLoanDetails(models.Model):
    _name = "book.loan.details"
    _description = "Book Loan Information"
    _inherit="mail.thread"
    issue_date = fields.Date(string="Isuue Date")
    return_date = fields.Date(string="Return Date")
    fine_amount = fields.Float(string="Fine Amount")
    status = fields.Selection(
        [
            ("onloan", "On Loan"),
            ("returned", "Returned"),
            ("overdue", "OverDue"),
        ],
        "Status",
    )
    member_id = fields.Many2one("member.details", string="Members")
    book_id = fields.Many2one("book.details", string="Books")
    library_id = fields.Many2one(
        "library.details", string="Library", related="member_id.library_id"
    )

    book_count = fields.Integer(compute="_compute_book_count")

    @api.constrains("fine_amount")
    def _check_fine_amount(self):
        if self.fine_amount < 0:
            raise ValidationError(_("Fine Amount should not be negative"))

    @api.onchange("status")
    def _onchange_status(self):
        if self.status == "returned":
            self.return_date = fields.Date.today()

    def _compute_book_count(self):
        for record in self:
            record.book_count = self.env["book.details"].search_count(
                [("bookloan_ids", "=", record.id)]
            )

    def books_count(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Count Book",
            "view_mode": "tree,form",
            "res_model": "book.details",
            "target": "current",
            "domain": [("bookloan_ids", "=", self.id)],
        }
