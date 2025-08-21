# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    odoo_tittle_name = fields.Char('Title Name', help="Setup System Tittle Name,which replace Odoo")
    odoo_website_url = fields.Char('Website Url', help="Setup System Website Url,which replace Odoo Url")
    show_login_powered_by = fields.Char('Show Login Powered By', help="Setup System To show Powered by on Login")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        odoo_tittle_name = ir_config.get_param('odoo_tittle_name', default='ITeSolution Software Services')
        odoo_website_url = ir_config.get_param('odoo_website_url', default='https://www.itesolution.co.in')
        show_login_powered_by = ir_config.get_param('show_login_powered_by', default='True')
        res.update(
            odoo_tittle_name=odoo_tittle_name,
            odoo_website_url=odoo_website_url,
            show_login_powered_by=show_login_powered_by
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("odoo_tittle_name", self.odoo_tittle_name or "")
        ir_config.set_param("odoo_website_url", self.odoo_website_url or "")
        ir_config.set_param("show_login_powered_by", self.show_login_powered_by or "")
