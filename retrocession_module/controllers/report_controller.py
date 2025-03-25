from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class RetrocessionReportController(http.Controller):
    @http.route('/odoo/retrocession/report/<int:report_id>', type='http', auth='user', website=True)
    def render_retrocession_report(self, report_id, **kwargs):
        _logger.info(f"Rendering HTML report for ID: {report_id}")
        retrocession = request.env['retrocession.import'].browse(report_id)
        if not retrocession.exists():
            _logger.warning(f"Retrocession record {report_id} not found")
            return request.not_found()
        html = request.env['ir.qweb']._render(
            'retrocession_module.retrocession_report_template',
            {
                'docs': retrocession,
                'user': request.env.user,
            }
        )
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])
    
    @http.route('/odoo/retrocession/reportpdf/<int:report_id>', type='http', auth='user')
    def render_retrocession_pdf(self, report_id, **kwargs):
        _logger.info(f"Rendering PDF report for ID: {report_id}")
        retrocession = request.env['retrocession.import'].browse(report_id)
        if not retrocession.exists():
            _logger.warning(f"Retrocession record {report_id} not found")
            return request.not_found()

        pdf, _ = request.env.ref('retrocession_module.action_report_retrocession_pdf')._render_qweb_pdf(retrocession.ids)

        return request.make_response(pdf, headers=[
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', f'inline; filename=retrocession_{retrocession.id}.pdf'),
        ])
