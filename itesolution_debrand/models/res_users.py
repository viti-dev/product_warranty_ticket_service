from odoo import models, fields


class Users(models.Model):
    _inherit = 'res.users'

    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in ITeSolution Software Services')],
        'Notification', required=True, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Handle by Emails: notifications are sent to your email address\n"
             "- Handle in ITeSolution Software Services: notifications appear in your ITeSolution Software Services Inbox")
    odoobot_state = fields.Selection(
        [
            ('not_initialized', 'Not initialized'),
            ('onboarding_emoji', 'Onboarding emoji'),
            ('onboarding_attachement', 'Onboarding attachement'),
            ('onboarding_command', 'Onboarding command'),
            ('onboarding_ping', 'Onboarding ping'),
            ('idle', 'Idle'),
            ('disabled', 'Disabled'),
        ], string="ITeSolution Software Services Status", readonly=True, required=False)
       