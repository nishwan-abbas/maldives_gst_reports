# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    # Inherit the res.company model
    _inherit = 'res.company'

    # Add a field to record 'activity_no' in the res.company model
    activity_no = fields.Char(string='Tax Activity Number')
