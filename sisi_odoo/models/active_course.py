from odoo import fields, models
import datetime


class ActiveCourse(models.Model):
    _name = 'sisi.active.course'
    _description = 'Active Course Management'

    year = fields.Integer(string='Academic Year',
                          required=True,
                          default=lambda self: datetime.datetime.now().year)
    season = fields.Selection([
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
    ],
        string='Season',
        required=True)

    session = fields.Integer(string="Sem/Lab Count",
                             required=True,
                             default=1)
    count = fields.Integer(string="Week count",
                           default=16,
                           required=True)
    duration = fields.Selection([
        ('90', '90 minutes'),
        ('135', '135 minutes'),
        ('180', '180 minutes'),
    ])

    max_students = fields.Integer(string='Maximum Students',
                                  required=True)
    students_per_session = fields.Integer(string='Maximum Student per session',
                                          default=0)
    is_active = fields.Boolean(string='Is Active',
                               default=True)

    course_id = fields.Many2one(comodel_name='sisi.course')
    teacher_id = fields.Many2many(comodel_name='sisi.teacher')

    def name_get(self):
        result = []
        result = []
        for rec in self:
            course_name = rec.course_id.display_name if rec.course_id else "No Course"
            teacher_names = ", ".join(rec.teacher_id.mapped("display_name")) if rec.teacher_id else "No Teacher"

            display_name = f"{course_name} ({teacher_names})"
            result.append((rec.id, display_name))
        return result
