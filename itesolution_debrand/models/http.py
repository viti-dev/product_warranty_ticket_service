# -*- coding: utf-8 -*-
import logging
import json
from odoo.tools import ustr, consteq, frozendict, pycompat, unique, date_utils
from odoo.http import JsonRequest, AuthenticationError, SessionExpiredException, ustr, request, serialize_exception, Response

_logger = logging.getLogger(__name__)


def _json_response(self, result=None, error=None):
    config_parameter = request.env['ir.config_parameter'].sudo()
    title_name = config_parameter.get_param('odoo_tittle_name', 'ITeSolution Software Services')
    response = {
        'jsonrpc': '2.0',
        'id': self.jsonrequest.get('id')
        }
    if error is not None:
        error['message'] = error['message'].replace("Odoo", title_name)
        response['error'] = error
    if result is not None:
        response['result'] = result

    mime = 'application/json'
    body = json.dumps(response, default=date_utils.json_default)

    return Response(
        body, status=error and error.pop('http_status', 200) or 200,
        headers=[('Content-Type', mime), ('Content-Length', len(body))]
    )

setattr(JsonRequest,'_json_response',_json_response)
