from odoo import fields, models


class Assignment(models.Model):
    _name = 'sisi.assignment'
    _description = 'Assignment Management'

    name = fields.Char(string='Assignment Name', required=True)
    description = fields.Text(string='Assignment Description')
    due_date = fields.Date(string='Due Date', required=True)
    max_score = fields.Integer(string='Maximum Score', required=True)
    attachments = fields.Many2many(
        'ir.attachment', string='Attachments')
    is_submittable = fields.Boolean(string='Is Submittable', default=False)
