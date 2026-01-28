from odoo import models, fields


class AssignmentItem(models.Model):
    _name = "sisi.assignment.item"
    _description = "Assignment Item Definition & Management"

    score = fields.Integer(string="Student's Score")
    attachment = fields.Many2one(
        'ir.attachment', string='Attachment')
