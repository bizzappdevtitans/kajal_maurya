from odoo import models, fields, api


class BookDetails(models.Model):
    _name = "book.details"
    _description = "Book Information"
    name = fields.Char(string="Title")
    author_id = fields.Many2one("author.details", "Author")
    genre = fields.Selection(
        [
            ("fiction", "Fiction"),
            ("non_fiction", "Non Fiction"),
            ("mystrey", "Mystrey"),
            ("other", "Other"),
        ],
        "Genre",
    )
    publication_date = fields.Date(string="Publication Date", help="Choose a date")
    available_copies = fields.Integer(string="Available Copies", default=1)
    avg_rating = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Low"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        string="Average Rating",
    )
    date_added_to_library = fields.Datetime(
        string="Date Added To Library", default=lambda self: fields.Datetime.now()
    )
    is_available = fields.Boolean(string="Is Available", default=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancel"),
        ],
        default="draft",
        string="Status",
        required=True,
    )

    book_completion = fields.Float(string="Book Completion")

    book_condition = fields.Selection([("new", "New"), ("used", "Used")], default="new")

    color = fields.Char(string="Color", help="Choose your color")

    color_picker = fields.Integer(string="Color Picker")


    def action_draft(self):
        self.write({"state": "draft"})

    def action_in_progress(self):
        for record in self:
            if record.state == "draft":
                self.write({"state": "in_progress"})

    def action_done(self):
        self.write({"state": "done"})

    def action_cancel(self):
        self.write({"state": "cancel"})



    def action_toggle_availability(self):
        self.write({"is_available": not self.is_available})





