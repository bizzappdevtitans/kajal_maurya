from odoo import models,fields

class MemberDetails(models.Model):
    _name="member.details"
    _description="Member Information"
    name=fields.Char(string="Name")
    address=fields.Text(string="Address")
    email=fields.Char(string="Email")
    subscription_id=fields.Integer(string="Subscription ID")
    total_book_taken=fields.Integer(string="Total Book Taken")
    submission_date=fields.Date(string="Due Date")
    library=fields.Many2one('library.details',"Library")
