# -*- coding: utf-8 -*-
import logging
import odoo
import odoo.modules.registry
from odoo.tools.translate import _
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request
from odoo.addons.web.controllers.home import Home, ensure_db, SIGN_UP_REQUEST_PARAMS


_logger = logging.getLogger(__name__)


class Home(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.update_env(user=odoo.SUPERUSER_ID)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(
                    request.params['login'],
                    request.params['password']
                )
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        config_parameter = request.env['ir.config_parameter'].sudo()
        values['odoo_tittle_name'] = config_parameter.get_param('odoo_tittle_name', 'ITeSolution Software Services')
        values['odoo_website_url'] = config_parameter.get_param('odoo_website_url', 'https://www.itesolution.co.in')
        values['show_login_powered_by'] = config_parameter.get_param('show_login_powered_by', 'False')

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response