from odoo import http
from odoo.http import request

class RetrocessionReportController(http.Controller):
    @http.route('/retrocession/report/<int:report_id>', type='http', auth='user', website=True)
    def render_retrocession_report(self, report_id, **kwargs):
        # Fetch the record
        retrocession = request.env['retrocession.import'].browse(report_id)
        if not retrocession.exists():
            return request.not_found()

        # Render the QWeb template as HTML
        html = request.env['ir.qweb']._render(
            'retrocession_module.retrocession_report_template',
            {'docs': retrocession}
        )

        # Return the HTML response
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])