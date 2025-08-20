from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    serial_number = fields.Char(
        string="Serial Number",
        help="Enter the serial/lot number. Product and warranty details will be auto-filled."
    )
    lot_id = fields.Many2one("stock.lot", string="Lot", readonly=True)
    product_id = fields.Many2one("product.product", string="Product", readonly=True)
    product_description = fields.Text(string="Product Description", store=True, readonly=True)

    warranty_period = fields.Integer(string="Warranty Period (Months)", store=True, readonly=True)
    warranty_start_date = fields.Date(string="Start Date", store=True, readonly=True)
    warranty_end_date = fields.Date(string="End Date", store=True, readonly=True)

    partner_id = fields.Many2one("res.partner", related="lot_id.customer_id", store=True, readonly=True)

    @api.onchange('serial_number')
    def _onchange_serial_number(self):
        """ Validate serial number and auto-fill fields """
        for rec in self:
            if rec.serial_number:
                lot = self.env['stock.lot'].search([('name', '=', rec.serial_number)], limit=1)
                if not lot:
                    raise UserError(_("Invalid Serial Number entered. Please check again."))

                # Restrict: User cannot use another customer's serial number
                if lot.customer_id and rec.partner_id and lot.customer_id.id != rec.partner_id.id:
                    raise UserError(_(
                        "This Serial Number belongs to another customer: %s. "
                        "You cannot create a ticket for another customer's product."
                    ) % (lot.customer_id.display_name))

                rec.lot_id = lot.id
                rec.product_id = lot.product_id.id
                rec.product_description = lot.product_id.display_name

                # Fill customer details
                if lot.customer_id:
                    rec.partner_id = lot.customer_id.id

                if hasattr(lot, "customer_email") and lot.customer_email:
                    rec.email_cc = lot.customer_email

                # Warranty details
                if lot.product_id.is_warranty_period or lot.warranty_start_date:
                    rec.warranty_period = lot.warranty_period
                    rec.warranty_start_date = lot.warranty_start_date
                    rec.warranty_end_date = lot.warranty_start_date + relativedelta(months=lot.warranty_period)

    # ========== SLA Check (CRON) ==========
    def _check_cron_sla(self):
        """Cron to check SLA deadlines and send reminders/escalations"""
        now = fields.Datetime.now()

        # 1. Reminder: 30 min before SLA deadline
        reminder_tickets = self.search([
            ("sla_deadline", "!=", False),
            ("sla_deadline", "<=", now + timedelta(minutes=30)),
            ("sla_deadline", ">", now)
        ])
        for ticket in reminder_tickets:
            template = self.env.ref("service_management.mail_template_sla_reminder", raise_if_not_found=False)
            if template:
                template.send_mail(ticket.id, force_send=True)

        # 2. Escalation: SLA breached (deadline passed 15 min ago)
        escalated_tickets = self.search([
            ("sla_deadline", "!=", False),
            ("sla_deadline", "<", now - timedelta(minutes=15)),
        ])
        for ticket in escalated_tickets:
            template = self.env.ref("service_management.mail_template_sla_escalation", raise_if_not_found=False)
            if template:
                template.send_mail(ticket.id, force_send=True)

    # ========== Ticket Creation ==========
    def create(self, vals):
        ticket = super(HelpdeskTicket, self).create(vals)

        if ticket.partner_id and ticket.partner_id.email:
            template = self.env.ref("service_management.mail_template_helpdesk_ticket_created", raise_if_not_found=False)
            if template:
                template.send_mail(ticket.id, force_send=True)
                print("============================= Email Sent Successfully")

        return ticket

    # ========== Ticket Update ==========
    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)

        if 'stage_id' in vals:
            self._send_stage_notification()

        return res

    def _send_stage_notification(self):
        print("================= Stage Change Email Sent")
        template = self.env.ref('service_management.email_template_service_ticket_stage_changed', raise_if_not_found=False)
        for ticket in self:
            if template:
                template.send_mail(ticket.id, force_send=True)
