from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    

    serial_number = fields.Char(
        string="Serial Number",
        help="Select the serial/lot. Product and description will be auto-filled."
    )
    # lot_id = fields.Many2one("stock.lot", string="Lot", readonly=True)
    # product_id = fields.Many2one("product.product", string="Product",  readonly=True)
    # product_description = fields.Text(string="Product Description", store=True, readonly=True)
   
    # warranty_period = fields.Integer(string="Warranty Period (Months)", store=True, readonly=True)
    # warranty_start_date = fields.Date(string="Start Date", store=True, readonly=True)
    # warranty_end_date = fields.Date(string="End Date", store=True, readonly=True)
    # partner_id = fields.Many2one("res.partner", related="lot_id.customer_id", store=True, readonly=True)

    # @api.onchange('serial_number')
    # def _onchange_serial_number(self):
    #     """ Validate serial and auto-fill fields """
    #     for rec in self:
    #         if rec.serial_number:
    #             lot = self.env['stock.lot'].search([('name', '=', rec.serial_number)], limit=1)
    #             if not lot:
    #                 raise UserError(_("Invalid Serial Number entered. Please check again."))

    #             rec.lot_id = lot.id
    #             rec.product_id = lot.product_id.id
    #             rec.product_description = lot.product_id.display_name

            
    #             if lot.customer_id:
    #                 rec.partner_id = lot.customer_id.id

    #             if lot.customer_email:
    #                 rec.email_cc = lot.customer_email

            
    #             if  lot.product_id.is_warranty_period or lot.warranty_start_date:
    #                 rec.warranty_period = lot.warranty_period
    #                 rec.warranty_start_date = lot.warranty_start_date
    #                 rec.warranty_end_date = lot.warranty_start_date + relativedelta(months=lot.warranty_period)

    lot_id = fields.Many2one("stock.lot", string="Lot", readonly=True)
    product_id = fields.Many2one("product.product", compute="_compute_from_lot", store=True)
    product_description = fields.Text(compute="_compute_from_lot", store=True)
    warranty_period = fields.Integer(compute="_compute_from_lot", store=True)
    warranty_start_date = fields.Date(compute="_compute_from_lot", store=True)
    warranty_end_date = fields.Date(compute="_compute_from_lot", store=True)

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # rec._set_values_from_serial()
        if ticket.partner_id and ticket.partner_id.email:
            template = self.env.ref("service_management.mail_template_helpdesk_ticket_created")
            template.send_mail(ticket.id, force_send=True)
            print("=============================Email Sent Successfully")
        return rec
    
    def write(self, vals):
        res = super().write(vals)
        # self._set_values_from_serial()
        if 'stage_id' in vals:
            self._send_stage_notification()
        return res

    # def create(self, vals):
    #     ticket = super(HelpdeskTicket, self).create(vals)

        
    #     if ticket.partner_id and ticket.partner_id.email:
    #         template = self.env.ref("service_management.mail_template_helpdesk_ticket_created")
    #         template.send_mail(ticket.id, force_send=True)
    #         print("=============================Email Sent Successfully")

    #     return ticket
    
    # def write(self, vals):
    #     res = super(HelpdeskTicket, self).write(vals)
        
    #     if 'stage_id' in vals:
    #         self._send_stage_notification()
        
    #     return res
    
    def _set_values_from_serial(self):
        for rec in self:
            if rec.serial_number:
                lot = self.env['stock.lot'].search([('name', '=', rec.serial_number)], limit=1)
                if not lot:
                    raise UserError(_("Invalid Serial Number entered. Please check again."))
                if lot:
                    rec.lot_id = lot
                    rec.product_id = lot.product_id
                    rec.product_description = lot.product_id.display_name or ""
                    rec.partner_id = lot.customer_id
                    if lot.warranty_start_date and lot.warranty_period:
                        rec.warranty_period = lot.warranty_period
                        rec.warranty_start_date = lot.warranty_start_date
                        rec.warranty_end_date = lot.warranty_start_date + relativedelta(months=lot.warranty_period)

    
    # @api.depends("lot_id")
    # def _compute_from_lot(self):
    #     for rec in self:
    #         lot = rec.lot_id
    #         if lot:
    #             rec.product_id = lot.product_id
    #             rec.product_description = lot.product_id.display_name or ""
    #             rec.partner_id = lot.customer_id
    #             rec.warranty_period = lot.warranty_period or 0
    #             rec.warranty_start_date = lot.warranty_start_date
    #             rec.warranty_end_date = (
    #                 lot.warranty_start_date + relativedelta(months=lot.warranty_period)
    #                 if lot.warranty_start_date and lot.warranty_period
    #                 else False
    #             )
    #         else:
    #             rec.product_id = False
    #             rec.product_description = ""
    #             rec.partner_id = False
    #             rec.warranty_period = 0
    #             rec.warranty_start_date = False
    #             rec.warranty_end_date = False

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

    
         
