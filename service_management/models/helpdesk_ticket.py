
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    # serial_number = fields.Char(
    #     string="Serial Number",
    #     help="Select the serial/lot. Product and description will be auto-filled."
    # )
    # lot_id = fields.Many2one("stock.lot", string="Lot", readonly=True)
    # product_id = fields.Many2one("product.product", string="Product",  readonly=True)
    # product_description = fields.Text(string="Product Description", store=True, readonly=True)
    #
    # warranty_period = fields.Integer(string="Warranty Period (Months)", store=True, readonly=True)
    # warranty_start_date = fields.Date(string="Start Date", store=True, readonly=True)
    # warranty_end_date = fields.Date(string="End Date", store=True, readonly=True)
    # partner_id = fields.Many2one("res.partner", related="lot_id.customer_id", store=True, readonly=True)

    serial_number = fields.Char("Serial Number")
    lot_id = fields.Many2one("stock.lot", string="Lot")
    product_id = fields.Many2one("product.product", string="Product")
    product_description = fields.Text("Product Description")

    warranty_period = fields.Integer("Warranty Period (Months)")
    warranty_start_date = fields.Date("Start Date")
    warranty_end_date = fields.Date("End Date")

    partner_id = fields.Many2one("res.partner", string="Customer")

    def _fill_from_serial(self, serial_number):
        """Helper: fetch lot and related data by serial, or reset if empty"""
        if not serial_number:
            # Clear all related fields if serial number removed
            return {
                "lot_id": False,
                "product_id": False,
                "product_description": False,
                "warranty_period": False,
                "warranty_start_date": False,
                "warranty_end_date": False,
                "partner_id": False,
            }

        lot = self.env["stock.lot"].search([("name", "=", serial_number)], limit=1)
        if not lot:
            raise UserError(_("Invalid Serial Number entered. Please check again."))
        return {
            "lot_id": lot.id,
            "product_id": lot.product_id.id,
            "product_description": lot.product_id.display_name,
            "warranty_period": lot.warranty_period,
            "warranty_start_date": lot.warranty_start_date,
            "warranty_end_date": lot.warranty_start_date + relativedelta(months=lot.warranty_period)
            if lot.warranty_start_date and lot.warranty_period else False,
            "partner_id": lot.customer_id.id if lot.customer_id else False,
        }

    @api.model
    def create(self, vals):
        if "serial_number" in vals:  # even if False
            vals.update(self._fill_from_serial(vals.get("serial_number")))

        ticket = super().create(vals)

        if ticket.partner_id and ticket.partner_id.email:
            template = self.env.ref("service_management.mail_template_helpdesk_ticket_created",
                                    raise_if_not_found=False)
            if template:
                template.send_mail(ticket.id, force_send=True)

        return ticket

    def write(self, vals):
        if "serial_number" in vals:  # even if False
            vals.update(self._fill_from_serial(vals.get("serial_number")))

        res = super().write(vals)

        if "stage_id" in vals:
            self._send_stage_notification()

        return res

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

    def _send_stage_notification(self):
        print("=================Email Sent")
        template = self.env.ref('service_management.email_template_service_ticket_stage_changed')
        for ticket in self:
            template.send_mail(ticket.id, force_send=True)

    def action_generate_fsm_task(self):
        self.ensure_one()
        if not self.partner_id and (self.partner_name or self.partner_email):
            self.partner_id = self._find_or_create_partner(self.partner_name, self.partner_email, self.company_id.id)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create a Field Service task'),
            'res_model': 'helpdesk.create.fsm.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'use_fsm': True,
                'default_helpdesk_ticket_id': self.id,
                'default_user_id': False,
                'default_partner_id': self.partner_id.id,
                'default_name': self.name,
                'default_project_id': self.team_id.sudo().fsm_project_id.id,
                'dialog_size': 'medium',
            }
        }


class HelpdeskCreateFSMTask(models.TransientModel):
    _inherit = 'helpdesk.create.fsm.task'

    def action_generate_and_view_task(self):
        self.ensure_one()
        new_task = self.action_generate_task()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks from Tickets'),
            'res_model': 'project.task',
            'res_id': new_task.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project.view_task_form2').id,
            'context': {
                'fsm_mode': True,
                'create': False,
                'default_helpdesk_ticket_id': self.helpdesk_ticket_id.id,  # ✅ fixed
            }
        }

    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string="Helpdesk Ticket",
        readonly=True
    )

    def _generate_task_values(self):
        self.ensure_one()
        values = super(HelpdeskCreateFSMTask, self)._generate_task_values()
        # ✅ Force link with the ticket
        if self.helpdesk_ticket_id:
            values['helpdesk_ticket_id'] = self.helpdesk_ticket_id.id
            # Also push description if empty
            if not values.get("description") and self.helpdesk_ticket_id.description:
                values['description'] = self.helpdesk_ticket_id.description
        return values

