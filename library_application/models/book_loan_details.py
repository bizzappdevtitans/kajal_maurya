from odoo import models,fields

class BookLoanDetails(models.Model):
    _name="book.loan.details"
    _description="Book Loan Information"
    issue_date=fields.Date(string="Isuue Date")
    return_date=fields.Date(string="Return Date")
    fine_amount=fields.Float(string="Fine Amount")
    status=fields.Selection(
        [
            ("onloan","On Loan"),
            ("returned","Returned"),
            ("overdue","OverDue"),

        ],
        "Status"
        )



