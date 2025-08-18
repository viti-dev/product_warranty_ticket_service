from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_warranty_period = fields.Boolean(
        string="Can Be Warranty", 
        default=True
        
    )