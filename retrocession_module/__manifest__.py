{
    "name": "Retrocession Management",
    "version": "1.1",
    "category": "Sales",
    "summary": "Gestion des rétrocessions à partir d'un fichier Excel, avec commission par client/distributeur",
    "depends": ["base", "sale"],
    "data": [
        "data/retrocession_models.xml",
        "security/ir.model.access.csv",
        "views/retrocession_views.xml",
        "reports/retrocession_report_template.xml",
        "reports/retrocession_report_action.xml",
    ],
    "installable": True,
    "application": True
}