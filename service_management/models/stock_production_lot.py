from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class StockProductionLot(models.Model):
    _inherit = "stock.lot"

    customer_id = fields.Many2one("res.partner", string="Customer")
    customer_email = fields.Char(related="customer_id.email", string="Customer Email", store=True, readonly=True)
    customer_phone = fields.Char(related="customer_id.phone", string="Customer Phone", store=True, readonly=True)

    warranty_start_date = fields.Date(string="Warranty Start Date")
    warranty_end_date = fields.Date(string="Warranty End Date" ,compute="_compute_warranty_end_date",store=True, readonly=True)
    warranty_period = fields.Integer(string="Warranty Period (Months)", default=0)

    @api.depends("warranty_start_date", "warranty_period")
    def _compute_warranty_end_date(self):
        for rec in self:
            if rec.warranty_start_date and rec.warranty_period:
                rec.warranty_end_date = rec.warranty_start_date + relativedelta(months=rec.warranty_period)
            else:
                rec.warranty_end_date = False
