from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        config_parameter = request.env['ir.config_parameter'].sudo()
        result['odoo_tittle_name'] = config_parameter.get_param('odoo_tittle_name', 'ITeSolution Software Services')
        return result
