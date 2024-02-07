from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BookDetails(models.Model):
    _name = "book.details"
    _description = "Book Information"
    _order = "sequence_handle"

    name = fields.Char(string="Title", required=True)
    author_ids = fields.Many2many(
        comodel_name="author.details",
        relation="book_author_relation",
        string="Authors",
        column1="books_written",
        column2="author_ids",
    )
    genre = fields.Selection(
        [
            ("fiction", "Fiction"),
            ("non_fiction", "Non Fiction"),
            ("mystrey", "Mystrey"),
            ("other", "Other"),
        ],
        string="Genre",
    )
    publication_date = fields.Date(
        string="Publication Date", help="Choose a date", default=fields.Date.today()
    )
    available_copies = fields.Integer(string="Available Copies")
    total_copies = fields.Integer(string="Total Copies")
    price = fields.Float(string="Price")
    avg_rating = fields.Selection(
        [
            ("0", "Normal"),
            ("1", "Low"),
            ("2", "High"),
            ("3", "Very High"),
        ],
        string="Average Rating",
        default="0",
        required=True,
    )
    date_added_to_library = fields.Date(
        string="Date Added To Library", default=fields.Date.today()
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
    book_condition = fields.Selection(
        [("new", "New"), ("used", "Used"), ("damage", "Damaged")],
        string="Book Condition",
        default="new",
        required=True,
    )
    progress_book_condition = fields.Integer(
        string="Progress", compute="_compute_progress"
    )
    library_id = fields.Many2one(comodel_name="library.details", string="Library")
    bookloan_ids = fields.One2many(
        comodel_name="book.loan.details", inverse_name="book_id", string="Book Loan"
    )
    sequence_no = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    book_image = fields.Image(string="Book Image")
    availability_message = fields.Text(string="Availability Message", readonly=True)
    sequence_handle = fields.Integer(string="Sequence", default="1")

    # action for change in 'price' field value according to 'book_condition'
    def action_new(self):
        self.write({"book_condition": "new"})

    def action_used(self):
        for record in self:
            self.price = self.price - 50
            self.write({"book_condition": "used"})

    def action_damage(self):
        for record in self:
            if record.book_condition == "used":
                self.price = self.price - 100
                self.write({"book_condition": "damage"})

    # action for toggle button for 'is_available' field
    def action_toggle_availability(self):
        self.write({"is_available": not self.is_available})

    # method for changing the value of progressbar according to book_condition
    @api.depends("book_condition")
    def _compute_progress(self):
        for record in self:
            if record.book_condition == "damage":
                progress_book_condition = 50
            elif record.book_condition == "used":
                progress_book_condition = 75
            elif record.book_condition == "new":
                progress_book_condition = 100
            else:
                progress_book_condition = 0
            record.progress_book_condition = progress_book_condition

    # constrain for name field
    _sql_constraints = [
        ("unique_name", "unique (name)", "Title must be unique."),
    ]

    # validation of 'publication date'
    @api.constrains("publication_date")
    def validate_publication_date(self):
        for record in self:
            if (
                record.publication_date
                and record.publication_date > fields.Date.today()
            ):
                raise ValidationError(_("The entered date is not acceptable"))

    # validation of 'publication date' with 'date added to library'
    @api.onchange("publication_date", "date_added_to_library")
    def _onchange_date_added_to_library(self):
        if self.date_added_to_library < self.publication_date:
            return {
                "warning": {
                    "title": _("Validation Error"),
                    "message": _("The book can't be added before getting published"),
                }
            }

    # validation for available copies
    @api.onchange("available_copies", "total_copies")
    def _onchange_available_copies(self):
        if self.available_copies > self.total_copies:
            raise ValidationError("Available Copies can't be greater than Total Copies")

    # Sequence for book.details
    @api.model
    def create(self, vals):
        if vals.get("sequence_no", _("New")) == _("New"):
            vals["sequence_no"] = self.env["ir.sequence"].next_by_code(
                "book.details"
            ) or _("New")
        result = super(BookDetails, self).create(vals)
        return result

    # validation of 'price'
    @api.constrains("price")
    def _check_price(self):
        if self.price < 0:
            raise ValidationError(_("Book Price should not be negative"))

    # method to chage the val;ue of 'avg_rating' on the basis of 'price'
    def write(self, vals):
        if "price" in vals:
            price = vals.get("price")
            if price >= 650:
                self.avg_rating = "2"
        return super(BookDetails, self).write(vals)

    # method to raise user error when user try to delete the related record
    def unlink(self):
        if self.author_ids:
            raise UserError("You can't delete the record")
        return super(BookDetails, self).unlink()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s - %s" % (record.name, record.genre)))
        return result

    @api.model
    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if name:
            args += [
                "|",
                ("name", operator, name),
                ("genre", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(BookDetails, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        args += [
            "|",
            ("genre", "=", "fiction"),
            ("genre", "=", "non_fiction"),
        ]
        return super(BookDetails, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    def read(self, fields, load="_classic_read"):
        result = super(BookDetails, self).read(fields=fields, load=load)
        for record in result:
            if "is_available" in record and record["is_available"]:
                record["availability_message"] = "This book is available"
            else:
                record["availability_message"] = "This book is currently unavailable"
        return result
