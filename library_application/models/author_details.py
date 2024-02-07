from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AuthorDetails(models.Model):
    _name = "author.details"
    _description = "Author Information"
    _order = "sequence_handle"

    name = fields.Char(string="Author Name", required=True)
    biography = fields.Char(string="Biography")
    nationality = fields.Char(string="Nationality")
    email = fields.Char(string="Email")
    award_received = fields.Text(string="Award Received")
    birthdate = fields.Date(string="Birthday")
    sequence_no = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    books_written = fields.Many2many(
        comodel_name="book.details",
        string="Books Written",
        relation="author_book_relation",
        column1="author_ids",
        column2="books_written",
    )
    total_books_written = fields.Integer(
        string="Total Books Written", compute="_compute_total_books_written"
    )
    color = fields.Integer(string="Color")
    sequence_handle = fields.Integer(string="Sequence", default="1")

    # method for total book written count
    @api.depends("books_written")
    def _compute_total_books_written(self):
        for record in self:
            record.total_books_written = len(record.books_written)

    # validation for total book written
    @api.constrains("total_books_written")
    def _check_total_books_written(self):
        if self.total_books_written < 0:
            raise ValidationError(_("Total Books written should not be negative"))

    # Sequence for author.details
    @api.model
    def create(self, vals):
        if vals.get("sequence_no", _("New")) == _("New"):
            vals["sequence_no"] = self.env["ir.sequence"].next_by_code(
                "author.details"
            ) or _("New")
        result = super(AuthorDetails, self).create(vals)
        return result

    # method to capitalize the author name

    def write(self, vals):
        if "name" in vals:
            vals["name"] = vals["name"].capitalize()
            print(vals)
        return super(AuthorDetails, self).write(vals)

    # method to raise user error when user try to delete the linked records
    def unlink(self):
        if self.books_written:
            raise UserError("You can't delete the records")
        return super(AuthorDetails, self).unlink()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "%s - %s" % (record.name, record.nationality)))
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
                ("nationality", operator, name),
            ]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return super(LibraryDetails, self)._name_search(
            name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        args += [
            "|",
            ("nationality", "=", "American"),
            ("nationality", "=", "British"),
        ]
        return super(AuthorDetails, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
