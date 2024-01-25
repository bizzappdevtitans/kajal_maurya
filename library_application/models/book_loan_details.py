from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BookLoanDetails(models.Model):
    _name = "book.loan.details"
    _description = "Book Loan Information"
    _rec_name = "book_id"

    issue_date = fields.Date(string="Isuue Date")
    return_date = fields.Date(string="Return Date")
    due_date = fields.Date(string="Due Date")
    fine_amount = fields.Float(string="Fine Amount")
    status = fields.Selection(
        [
            ("onloan", "On Loan"),
            ("returned", "Returned"),
            ("overdue", "OverDue"),
        ],
        string="Status",
        default="returned",
        required=True,
    )
    member_id = fields.Many2one(comodel_name="member.details", string="Members")
    book_id = fields.Many2one(comodel_name="book.details", string="Books")
    library_id = fields.Many2one(
        comodel_name="library.details", string="Library", related="member_id.library_id"
    )

    book_count = fields.Integer(compute="_compute_book_count")

    # validation of ' fine amount'

    @api.constrains("fine_amount")
    def _check_fine_amount(self):
        if self.fine_amount < 0:
            raise ValidationError(_("Fine Amount should not be negative"))

    # method for changing the value of return_date on the basis of status

    @api.onchange("status")
    def _onchange_status(self):
        if self.status == "returned":
            self.return_date = fields.Date.today()

    # smart button implementation

    def _compute_book_count(self):
        for record in self:
            record.book_count = self.env["book.details"].search_count(
                [("bookloan_ids", "=", record.id)]
            )

    def books_count(self):
        if self.book_count == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Books",
                "view_mode": "form",
                "res_model": "book.details",
                "target": "current",
                "res_id": self.book_id.id,
            }
        else:
            return {
                "type": "ir.actions.act_window",
                "name": "Books",
                "view_mode": "tree,form",
                "res_model": "book.details",
                "target": "current",
                "domain": [("bookloan_ids", "=", self.id)],
            }

    """method for changing the value of 'available_copies' and 'is_available' field
    on the basis of status"""

    @api.onchange("status")
    def _onchange_status(self):
        if self.status == "onloan":
            self.book_id.available_copies -= 1
            if self.book_id.available_copies < 2:
                self.book_id.is_available = False
            else:
                self.book_id.is_available = True
        elif self.status == "overdue":
            self.book_id.available_copies = self.book_id.available_copies
            if self.book_id.available_copies < 2:
                self.book_id.is_available = False
            else:
                self.book_id.is_available = True
        else:
            self.book_id.available_copies += 1
