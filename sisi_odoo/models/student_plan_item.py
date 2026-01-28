from odoo import fields, models


class StudentPlanItem(models.Model):
    _name = "sisi.student.plan.item"
    _description = "Student Plan Item Definition & Management"

    year = fields.Integer(string="Year")
    season = fields.Selection([
        ('fall', 'Fall'),
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
    ],
        required=True)
    status = fields.Selection([
        ('planned', 'Planned'),
        ('studying', 'Studying'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('removed', 'Removed'),
    ],
        default='planned',
        readonly=True)

    student_id = fields.Many2one(comodel_name='sisi.student')
    course_id = fields.Many2one(comodel_name="sisi.course")
    grade_id = fields.Many2one(comodel_name="sisi.grade")
