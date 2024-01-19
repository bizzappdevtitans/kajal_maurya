from odoo import models, fields


class AuthorDetails(models.Model):
    _name = "author.details"
    _description = "Author Information"
    name = fields.Char(string="Author Name", required=True)
    book_ids = fields.One2many("book.details", "author_id", string="Books")
    bio = fields.Char(string="Biography")
    book_count = fields.Integer(string="Book", compute="compute_book_count")

    def _compute_book_count(self):
        for record in self:
            book_count = self.env["book.details"].search_count(
                [("author_id", "=", record.id)]
            )
        record.book_count = book_count

    def books_count(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Count Book",
            "view_mode": "tree,form",
            "res_model": "book.details",
            "target": "current",
            "domain": [("author_id", "=", self.id)],
        }
