from odoo import models, fields

class Course(models.Model):
    _name = 'demo_school.course'
    _description = 'Course'

    name = fields.Char(
        string='Course Name',
        required=True,
        help='Name of the course'
    )

    teacher_ids = fields.Many2many(
        'demo_school.teacher',
        'course_teacher_rel',
        'course_id',
        'teacher_id',
        string='Teachers',
        help='Select teachers who will teach this course'
    )
