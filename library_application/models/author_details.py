from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AuthorDetails(models.Model):
    _name = "author.details"
    _description = "Author Information"
    _inherit="mail.thread"
    name = fields.Char(string="Author Name", required=True)
    biography = fields.Char(string="Biography")
    nationality = fields.Char(string="Nationality")
    email = fields.Char(string="Email")
    award_received = fields.Text(string="Award Received")
    birthdate = fields.Date(string="Birthday")
    books_written = fields.One2many("book.details", "authors", string="Books Written")
    total_books_written = fields.Integer(
        string="Total Books Written", compute="_compute_total_books_written"
    )


    @api.depends("books_written")
    def _compute_total_books_written(self):
        for record in self:
            record.total_books_written = len(record.books_written)

    @api.constrains("total_books_written")
    def _check_total_books_written(self):
        if self.total_books_written < 0:
            raise ValidationError(_("Total Books written should not be negative"))


