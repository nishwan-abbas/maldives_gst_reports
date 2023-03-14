# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    # Inherit the account.move model to add custom fields and methods
    _inherit = 'account.move'

    # Define custom fields to store GST related information to Move
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items')
    partner_tin = fields.Char(string='Partner TIN', compute='_compute_partner_tin', store=True)
    activity_no = fields.Char(string='Activity No.', compute='_compute_activity_no', store=True)
    gst_supply = fields.Monetary(string='GST Supply', compute='_compute_gst_supply', store=True)
    zero_rated = fields.Monetary(string='Zero Rated', compute='_compute_zero_rated', store=True)
    tax_exempted = fields.Monetary(string='Tax Exempted', compute='_compute_tax_exempted', store=True)
    gst_6_percent = fields.Monetary(string='GST 6% Total', compute='_compute_gst_6_percent', store=True)
    gst_8_percent = fields.Monetary(string='GST 8% Total', compute='_compute_gst_8_percent', store=True)
    gst_12_percent = fields.Monetary(string='GST 12% Total', compute='_compute_gst_12_percent', store=True)
    gst_16_percent = fields.Monetary(string='GST 16% Total', compute='_compute_gst_16_percent', store=True)
    # gst_total = fields.Monetary(string='All GST Total', compute='_compute_gst_total', store=True)
    
    # Custom fields for use in Tourism Tax Returns
    service_charge = fields.Monetary(string='Service Charge 10% Total', compute='_compute_service_charge', store=True)
    taxable_amount = fields.Monetary(string='Taxable Amount', compute='_compute_taxable_amount', store=True)
    green_tax = fields.Monetary(string='Green Tax', compute='_compute_green_tax', store=True)

    # DEFINE CUSTOM METHODS TO COMPUTE THE VALUES OF GST RELATED FIELDS
    @api.depends('company_id')
    def _compute_activity_no(self):
        # retrieve the activity number of the company
        for move in self:
            move.activity_no = move.company_id.activity_no
            if not move.activity_no:
                move.activity_no = ''

    @api.depends('partner_id.vat')
    def _compute_partner_tin(self):
        for move in self:
            move.partner_tin = move.partner_id.vat

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_line_id.amount_type', 'line_ids.tax_line_id.amount')
    def _compute_gst_supply(self):
        # compute the GST supply value for the move
        for move in self:
            # get the tax rates for 6%, 8%, 12%, and 16%
            tax_rates = [6, 8, 12, 16]

            # initialize the GST supply variables for each tax rate
            gst_supply_dict = {
                6: 0,
                8: 0,
                12: 0,
                16: 0,
            }

            # iterate through the line items to calculate the GST for each tax rate
            for line in move.line_ids:
                if line.tax_line_id.amount_type == 'percent' and line.tax_line_id.amount in tax_rates:
                    # if the line has multiple tax rates applied, split the price subtotal
                    # among the relevant tax rates based on their proportions
                    tax_rate = line.tax_line_id.amount
                    tax_amount = line.price_subtotal * (tax_rate / 100)
                    gst_supply_dict[tax_rate] += tax_amount

            # calculate the total of all GST applied supplies
            gst_supply_total = sum(gst_supply_dict.values())

            # set the GST supply value for the move
            move.gst_supply = gst_supply_total

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_line_id.amount_type', 'line_ids.tax_line_id.amount')
    def _compute_zero_rated(self):
        # compute the zero-rated value for the move
        for move in self:
            # iterate through the line items to find all line items where a 0% tax is applied
            zero_rated_total = sum(line.price_subtotal for line in move.line_ids if line.tax_line_id.amount == 0)
            
            # set the zero-rated value for the move
            move.zero_rated = zero_rated_total

    @api.depends('line_ids.price_subtotal', 'line_ids.tax_line_id.amount_type', 'line_ids.tax_line_id.amount')
    def _compute_tax_exempted(self):
        # compute the total value of line items where no percentage tax is applied
        for move in self:
            tax_exempted_total = sum(line.price_subtotal for line in move.line_ids if not line.tax_line_id.amount and not line.tax_line_id.price_include)
            
            # set the tax exempted total value for the move
            move.tax_exempted = tax_exempted_total

    @api.depends('line_ids.tax_line_id.amount', 'line_ids.tax_line_id.amount_type')
    def _compute_gst_6_percent(self):
        # compute the total GST for taxes calculated at 6%
        for move in self:
            gst_6_percent = sum(line.tax_line_id.amount for line in move.line_ids if line.tax_line_id.amount_type == 'percent' and line.tax_line_id.amount == 6)
            move.gst_6_percent = gst_6_percent

    @api.depends('line_ids.tax_line_id.amount', 'line_ids.tax_line_id.amount_type')
    def _compute_gst_8_percent(self):
        # compute the total GST for taxes calculated at 8%
        for move in self:
            gst_8_percent = sum(line.tax_line_id.amount for line in move.line_ids if line.tax_line_id.amount_type == 'percent' and line.tax_line_id.amount == 8)
            move.gst_8_percent = gst_8_percent

    @api.depends('line_ids.tax_line_id.amount', 'line_ids.tax_line_id.amount_type')
    def _compute_gst_12_percent(self):
        # compute the total GST for taxes calculated at 12%
        for move in self:
            gst_12_percent = sum(line.tax_line_id.amount for line in move.line_ids if line.tax_line_id.amount_type == 'percent' and line.tax_line_id.amount == 12)
            move.gst_12_percent = gst_12_percent

    @api.depends('line_ids.tax_line_id.amount', 'line_ids.tax_line_id.amount_type')
    def _compute_gst_16_percent(self):
        # compute the total GST for taxes calculated at 16%
        for move in self:
            gst_16_percent = sum(line.tax_line_id.amount for line in move.line_ids if line.tax_line_id.amount_type == 'percent' and line.tax_line_id.amount == 16)
            move.gst_16_percent = gst_16_percent

    @api.depends('amount_untaxed_signed')
    def _compute_service_charge(self):
        for move in self:
            move.service_charge = move.amount_untaxed_signed * 0.1

    @api.depends('amount_untaxed_signed', 'service_charge')
    def _compute_taxable_amount(self):
        for move in self:
            move.taxable_amount = sum([move.amount_untaxed_signed, move.service_charge])

    @api.depends('line_ids.quantity', 'line_ids.price_unit', 'line_ids.tax_ids')
    def _compute_green_tax(self):
        # compute the green tax value for the move
        for move in self:
            green_tax_total = 0
            for line in move.line_ids:
                for tax in line.tax_ids:
                    if tax.amount_type == 'fixed' and tax.name == 'Green Tax':
                        green_tax_total += line.quantity * line.price_unit * (tax.amount / 100)

            # set the green tax value for the move
            move.green_tax = green_tax_total

