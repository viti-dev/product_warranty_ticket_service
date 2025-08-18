# helpdesk_service_flow/models/fsm_order.py
from odoo import api, fields, models

class FSMOrder(models.Model):
    _inherit = "project.task"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Helpdesk Ticket", index=True)
    start_service_time = fields.Datetime("Service Start Time", readonly=True)
    start_latitude = fields.Float("Start Latitude", readonly=True)
    start_longitude = fields.Float("Start Longitude", readonly=True)
    video_call_url = fields.Char("Video Call URL")

    def action_start_service(self):
        """
        Call with context lat/lng from mobile:
        self.with_context(lat=18.52, lng=73.85).action_start_service()
        """
        lat = self.env.context.get("lat")
        lng = self.env.context.get("lng")
        for rec in self:
            rec.start_service_time = fields.Datetime.now()
            if lat is not None and lng is not None:
                rec.start_latitude = float(lat)
                rec.start_longitude = float(lng)
        return True

    def action_generate_video_call(self):
        for rec in self:
            rec.video_call_url = f"https://meet.jit.si/fsm_task_{rec.id}"
        return True
