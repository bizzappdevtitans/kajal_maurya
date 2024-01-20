from odoo import models,fields

class LibraryDetails(models.Model):
    _name="library.details"
    _description="Library Information"
    name=fields.Char(string="Name" ,required=True)
    address=fields.Text(string="Address")
    librarian=fields.Char(string="Librarian")
    founded_year=fields.Date(string="Founded year")
    email=fields.Char(string="Email")
    opening_hours=fields.Char(string="Opening Hours")
    total_books=fields.Integer(string="Total Books" ,compute="")
    member_count=fields.Integer(string="Member Count",compute="")
    subscription_fee=fields.Float(string="Subscription Fee")
    books=fields.One2many('book.details','library',"Books")
    member=fields.One2many('member.details','library',"Member")
