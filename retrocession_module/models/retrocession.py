from odoo import models, fields, api
from datetime import datetime
import pandas as pd
import base64
import io
import logging
_logger = logging.getLogger(__name__)

class RetrocessionLine(models.Model):
    _name = 'retrocession.line'
    _description = 'Ligne de rétrocession'

    date = fields.Date(string="Date")
    machine = fields.Char(string="Machine")
    machine_number = fields.Char(string="Machine ID")
    order_number = fields.Char(string="Numéro de commande")
    product_name = fields.Char(string="Produit")
    price_ttc = fields.Float(string="Prix TTC")
    price_ht = fields.Float(string="Prix HT")
    commission = fields.Float(string="Commission")
    retrocession_id = fields.Many2one('retrocession.import', string="Import")

class RetrocessionImport(models.Model):
    _name = 'retrocession.import'
    _description = 'Import rétrocessions'

    name = fields.Char(string="Import rétrocession", compute="_compute_name", store=True)
    import_file = fields.Binary(string="Fichier Excel")
    filename = fields.Char(string="Nom du fichier")
    partner_id = fields.Many2one('res.partner', string="Client")
    distributor_id = fields.Many2one('res.partner', string="Distributeur")
    x_comission_rate = fields.Float(
        string="Taux de commission",
        related="distributor_id.x_comission_rate",
        readonly=True,
    )
    x_iban = fields.Char(
        string="IBAN de reversement des commissions",
        related="partner_id.x_iban",
        readonly=True,
    )

    line_ids = fields.One2many('retrocession.line', 'retrocession_id', string="Lignes")
    date_start = fields.Date(string="Date de début", readonly=True)
    date_end = fields.Date(string="Date de fin", readonly=True)
    total_ht = fields.Float(string="Total HT", readonly=True)
    total_commission = fields.Float(string="Total commissions", readonly=True)
    total_ttc = fields.Float(string="Total TTC", readonly=True)
    confirmed = fields.Boolean(string="Confirmé", default=False)

    @api.depends('partner_id', 'distributor_id')
    def _compute_name(self):
        for rec in self:
            name_parts = [f"#{rec.id}" if rec.id else "#"]
            if rec.partner_id:
                name_parts.append(rec.partner_id.name)
            if rec.distributor_id:
                name_parts.append(rec.distributor_id.name)
            rec.name = " – ".join(name_parts)

    @api.depends('distributor_id')
    def _compute_x_comission_rate(self):
        for rec in self:
            rec.x_comission_rate = rec.distributor_id.x_comission_rate or 0.0

    @api.depends('partner_id')
    def _compute_x_comission_rate(self):
        for rec in self:
            rec.x_iban = rec.partner_id.x_iban or ''

    @api.onchange('x_comission_rate', 'line_ids')
    def _onchange_x_comission_rate(self):
        for rec in self:
            total_ht = total_ttc = total_comm = 0.0
            for line in rec.line_ids:
                # recalc commission on each line
                line.commission = (line.price_ht or 0.0) * x_comission_rate
                total_ht += line.price_ht or 0.0
                total_ttc += line.price_ttc or 0.0
                total_comm += line.commission
            rec.total_ht = total_ht
            rec.total_ttc = total_ttc
            rec.total_commission = total_comm


    def action_import_file(self):
        if not self.partner_id:
            return

        file_data = base64.b64decode(self.import_file)
        df = pd.read_excel(io.BytesIO(file_data))
        # Normalize column names (remove NBSP)
        df.columns = df.columns.str.replace('\xa0', ' ').str.strip()

        lines = []
        dates = []
        total_ht = total_ttc = total_comm = 0.0

        for _, row in df.iterrows():
            # Parse date from “Creation time”
            try:
                date = pd.to_datetime(row.get('Creation time'), dayfirst=True).date()
            except Exception:
                date = False

            price_ttc = row.get('Sales price') or 0.0
            price_ht = (row.get('Sales price') or 0.0) / 1.081

            commission = price_ht * (self.x_comission_rate or 0.0)

            # Ensure both values are strings
            machine_num = str(row.get('Device number') or '').strip()
            raw_order = str(row.get('Order number') or '').strip()

            # Strip prefix if it matches
            if raw_order.startswith(machine_num) and machine_num:
                order = raw_order[len(machine_num):]
            else:
                order = raw_order

            lines.append((0, 0, {
                'date': date,
                'machine': row.get('Device name'),
                'machine_number' : row.get('Device number'),
                'order_number': order,
                'product_name': row.get('Goods name'),
                'price_ht': price_ht,
                'price_ttc': price_ttc,
                'commission': commission,
            }))

            if date:
                dates.append(date)
            total_ht += price_ht
            total_ttc += price_ttc
            total_comm += commission

        self.line_ids = lines
        self.date_start = min(dates) if dates else False
        self.date_end = max(dates) if dates else False
        self.total_ht = total_ht
        self.total_ttc = total_ttc
        self.total_commission = total_comm
        self.confirmed = True

    
    
    def action_open_html(self):
        if not self.id:
            raise UserError(_("Veuillez d'abord enregistrer l'import avant d'ouvrir en HTML."))
        url = f'/odoo/retrocession/report/{self.id}'
        _logger.info(f"Opening HTML report for ID {self.id} at URL: {url}")
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
    
    def action_open_pdf(self):
        if not self.id:
            raise UserError(_("Veuillez d'abord enregistrer l'import avant d'ouvrir en HTML."))
        url = f'/odoo/retrocession/reportpdf/{self.id}'
        _logger.info(f"Opening PDF report for ID {self.id} at URL: {url}")
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }



class Partner(models.Model):
    _inherit = 'res.partner'

    x_comission_rate = fields.Float(string="Taux de commission (%)")
    import_ids = fields.One2many('retrocession.import', 'partner_id', string="Rétrocessions")
    retrocession_ids = fields.One2many(
        'retrocession.import', 
        'partner_id', 
        string="Rétrocessions", 
        readonly=True
    )