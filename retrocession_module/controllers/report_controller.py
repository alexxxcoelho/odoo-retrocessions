from odoo import http
from odoo.http import request
from playwright.sync_api import sync_playwright
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
    
    @http.route('/odoo/retrocession/pdf/<int:report_id>', type='http', auth='user')
    def generate_pdf_report(self, report_id, **kwargs):
        try:
            url = f"https://odoo.vpsp.ch/odoo/retrocession/report/{report_id}"
            _logger.info(f"Generating PDF for URL: {url}")

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox"],
                    executable_path="/usr/bin/chromium"  # Ajuste si le binaire est ailleurs
                )
                context = browser.new_context()
                page = context.new_page()
                page.goto(url, wait_until="networkidle")
                
                # Tu peux ajouter un `page.wait_for_selector()` ici si tu veux attendre un div spécifique
                pdf = page.pdf(format="A4", margin={"top": "10mm", "bottom": "10mm"})
                browser.close()

            return request.make_response(pdf, headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'inline; filename=retrocession_{report_id}.pdf')
            ])

        except Exception as e:
            _logger.exception("PDF generation failed")
            return request.make_response(
                f"<h1>Erreur lors de la génération du PDF</h1><pre>{str(e)}</pre>",
                headers=[('Content-Type', 'text/html')],
                status=500
            )