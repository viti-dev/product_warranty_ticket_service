# helpdesk_service_flow/models/helpdesk_team.py
from odoo import fields, models

class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    reminder_hours_before_breach = fields.Float(
        string="Reminder (hours before SLA breach)",
        default=1.0,
        help="Send reminder this many hours before the SLA deadline."
    )
    senior_manager_partner_id = fields.Many2one(
        "res.partner",
        string="Senior Manager (Escalation To)",
        help="Tickets that breach SLA will be escalated to this contact."
    )
    notify_management_partner_ids = fields.Many2many(
        "res.partner",
        string="Notify Management (Stage Emails)",
        help="These contacts are notified on each stage change."
    )
