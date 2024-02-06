from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BookLoanDetails(models.Model):
    _name = "book.loan.details"
    _description = "Book Loan Information"
    _order = "sequence_handle"
    _rec_name = "book_id"

    issue_date = fields.Date(string="Isuue Date")
    return_date = fields.Date(string="Return Date")
    due_date = fields.Date(string="Due Date")
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
    library_id = fields.Many2one(comodel_name="library.details", string="Library")
    book_count = fields.Integer(compute="_compute_book_count")
    sequence_no = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    sequence_handle = fields.Integer(string="Sequence", default="1")
    color = fields.Integer(string="Color")
    fine_amount=fields.Float(string="Fine Amount")

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

    def _compute_book_count(self):
        for record in self:
            record.book_count = self.env["book.details"].search_count(
                [("bookloan_ids", "=", record.id)]
            )

    # smart button implementation
    def action_book_count(self):
        if self.book_count == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Books",
                "view_mode": "form",
                "res_model": "book.details",
                "target": "new",
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

    # method for defining actions for returned button
    def action_returned(self):
        for record in self:
            record.write({"status": "returned"})
            if record.status == "returned":
                record.book_id.available_copies += 1
                record.return_date = fields.Date.today()
                if record.book_id.available_copies < 1:
                    record.book_id.is_available = False
                else:
                    record.book_id.is_available = True

    # method for defining actions for onloan button
    def action_onloan(self):
        for record in self:
            record.write({"status": "onloan"})
            if record.status == "onloan":
                record.book_id.available_copies -= 1
                if record.book_id.available_copies < 1:
                    record.book_id.is_available = False
                else:
                    record.book_id.is_available = True

    # method for defining actions for overdue button
    def action_overdue(self):
        for record in self:
            record.write({"status": "overdue"})
            if record.status == "overdue":
                record.book_id.available_copies = record.book_id.available_copies
                if record.book_id.available_copies < 1:
                    record.book_id.is_available = False
                else:
                    record.book_id.is_available = True

    # Sequence for bookloan.details
    @api.model
    def create(self, vals):
        if vals.get("sequence_no", _("New")) == _("New"):
            vals["sequence_no"] = self.env["ir.sequence"].next_by_code(
                "book.loan.details"
            ) or _("New")
        result = super(BookLoanDetails, self).create(vals)
        return result

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s - %s" % (record.sequence_no, record.status)))
        return result

    # @api.depends('fine_amount')
    # def _compute_fine_amount(self):
    #     params = self.env['ir.config_parameter'].sudo()
    #     fine_amount_param = int(params.get_param('library_application.fine_amount_param'))
    #     for record in self:
    #         record.fine_amount_param=fine_amount if fine_amount_param else 0

