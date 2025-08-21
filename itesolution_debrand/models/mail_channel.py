# -*- coding: utf-8 -*-
from odoo import api, models, _


class Channel(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def init_odoobot(self):
        if self.env.user.odoobot_state in [False, 'not_initialized']:
            odoobot_id = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
            channel_info = self.channel_get([odoobot_id])
            channel = self.browse(channel_info['id'])
            config_parameter = self.env['ir.config_parameter'].sudo()
            title_name = config_parameter.get_param('odoo_tittle_name', 'ITeSolution')
            message = _("Hello,<br/>%s's chat helps employees collaborate efficiently. I'm here to help you discover its features.<br/><b>Try to send me an emoji</b> <span class=\"o_odoobot_command\">:)</span>" %(title_name))
            channel.sudo().message_post(body=message, author_id=odoobot_id, message_type="comment", subtype_xmlid="mail.mt_comment")
            self.env.user.odoobot_state = 'onboarding_emoji'
            return channel
