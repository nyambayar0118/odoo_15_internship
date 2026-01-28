from odoo import models, fields


class School(models.Model):
    _name = 'sisi.school'
    _description = 'School Building Definition & Management'

    name = fields.Char(string='School Name', required=True)
    address = fields.Text(string='Address', required=True)
    established_date = fields.Date(string='Established Date')
    google_map_link = fields.Char(string='Google Map Link')
    google_map_embed_link = fields.Text(string='Google Map Embed Link')

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'School name must be unique.'),
    ]
