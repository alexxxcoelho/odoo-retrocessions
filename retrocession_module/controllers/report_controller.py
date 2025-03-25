from odoo import http
from odoo.http import request
import subprocess
import tempfile
import os
import requests
import base64
from datetime import datetime

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
        # Injecte la balise <base href="..."> juste après <head>
        base_href = '<base href="https://odoo.vpsp.ch" />'
        html = html.replace("<head>", f"<head>{base_href}")
        return request.make_response(html, headers=[
            ('Content-Type', 'text/html; charset=utf-8'),
        ])
    
    @http.route('/odoo/retrocession/pdf/<int:report_id>', type='http', auth='user')
    def generate_remote_pdf(self, report_id, **kwargs):
        url = "https://pdf.vpsp.ch/getpdf"
        session_id = request.httprequest.cookies.get('session_id')
        params = {
            "url": str(report_id),
            "auth": session_id
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            return f"❌ Erreur PDF: {response.status_code} - {response.text}"

        # Nom du fichier
        filename = f"retrocession_{report_id}.pdf"

        # Récupérer le modèle de rétrocession
        retro = request.env['retrocession.import'].browse(report_id)
        partner = retro.partner_id  # ou lier à ton contact selon ton modèle

        # Créer une pièce jointe
        attachment = request.env['ir.attachment'].sudo().create({
            'name': filename,
            'datas': base64.b64encode(response.content),
            'res_model': 'res.partner',
            'res_id': partner.id,
            'type': 'binary',
            'mimetype': 'application/pdf',
        })

        # Sujet du message
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        subject = f"{retro.name or filename} – PDF généré le {now}"

        # Envoyer un message dans le chatter du contact
        partner.message_post(
            body="📄 Le PDF de rétrocession a été généré automatiquement.",
            subject=subject,
            attachment_ids=[attachment.id]
        )

        # Retourner directement le PDF au navigateur
        return request.make_response(
            response.content,
            headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ]
        )