from odoo import models, fields


class AuthorDetails(models.Model):
    _name = "author.details"
    _description = "Author Information"
    name = fields.Char(string="Author_Name", required=True)
    book_ids = fields.One2many("book.details", "author_id", string="Books")
    bio=fields.Char(string="Biography")
