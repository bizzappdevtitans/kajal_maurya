from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class EventDetails(models.Model):
    _name = "event.details"
    _description = "Event Information"
    _order = "sequence_handle"

    name = fields.Char(string="Name", required=True)
    event_type = fields.Selection(
        [
            ("workshop", "Workshop"),
            ("general_talk", "General Talk"),
            ("author_visit", "Author Visit"),
            ("other", "Other"),
        ]
    )
    date_start = fields.Date(string="Date Start", default=fields.Date.today())
    date_end = fields.Date(string="Date End", default=fields.Date.today())
    speaker_id = fields.Many2one(comodel_name="author.details", string="Speaker")
    participant_ids = fields.Many2many(
        comodel_name="member.details", string="Participants"
    )
    registration_deadline = fields.Date(string="Reg. Deadline")
    registration_count = fields.Integer(
        string="Reg. Count", compute="_compute_registration_count"
    )
    sequence_no = fields.Char(
        string="Number",
        required=True,
        readonly=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )

    sequence_handle = fields.Integer(string="Sequence", default="1")

    # Sequence for event.details
    @api.model
    def create(self, vals):
        if vals.get("sequence_no", _("New")) == _("New"):
            vals["sequence_no"] = self.env["ir.sequence"].next_by_code(
                "event.details"
            ) or _("New")
        result = super(EventDetails, self).create(vals)
        return result

    # count of total ragistration

    @api.depends("participant_ids")
    def _compute_registration_count(self):
        for event in self:
            event.registration_count = len(event.participant_ids)

    # validation of 'start date' with 'end date'
    @api.onchange("date_start")
    def _onchange_start_date(self):
        if self.date_start > self.date_end:
            raise ValidationError(_(" start date should not be greater than end date"))

    def unlink(self):
        if self.participant_ids:
            raise UserError("You can't delete the records")
        return super(EventDetails, self).unlink()
