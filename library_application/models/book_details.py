from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BookDetails(models.Model):
    _name = "book.details"
    _description = "Book Information"
    _inherit = "mail.thread"
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
    available_copies = fields.Integer(string="Available Copies")
    avg_rating = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Low"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        string="Average Rating",
    )
    date_added_to_library = fields.Date(string="Date Added To Library")

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

    progress = fields.Integer(string="Progress", compute="_compute_progress")

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

    @api.depends("state")
    def _compute_progress(self):
        for record in self:
            if record.state == "draft":
                progress = 25
            elif record.state == "in_progress":
                progress = 50
            elif record.state == "done":
                progress = 100
            else:
                progress = 0
            record.progress = progress

    _sql_constraints = [
        ("unique_name", "unique (name)", "Title must be unique."),
        (
            "check_copies",
            "check (available_copies>0)",
            "Available copies must be non zero positive number .",
        ),
    ]

    @api.constrains("publication_date")
    def validate_publication_date(self):
        for record in self:
            if (
                record.publication_date
                and record.publication_date > fields.Date.today()
            ):
                raise ValidationError(_("The entered date is not acceptable"))

    @api.onchange("publication_date", "date_added_to_library")
    def _onchange_date_added_to_library(self):
        if (
            self.date_added_to_library
            and self.publication_date
            and self.date_added_to_library < self.publication_date
        ):
            return {
                "warning": {
                    "title": _(
                        "date added to library is lesser than publication date."
                    ),
                    "message": _("The book can't be added before getting published"),
                }
            }
