from odoo import fields, models


class Grade(models.Model):
    _name = 'sisi.grade'
    _description = 'SiSi Grade'

    o1 = fields.Integer()
    o2 = fields.Integer()
    letter_grade = fields.Selection([
        ('na', 'NA'),
        ('a+', 'A+'),
        ('a', 'A'),
        ('b+', 'B+'),
        ('b', 'B'),
        ('b-', 'B-'),
        ('c+', 'C+'),
        ('c', 'C'),
        ('c-', 'C-'),
        ('d', 'D'),
        ('d-', 'D-'),
        ('f', 'F'),
        ('s', 'S'),
        ('u', 'U'),
        ('g', 'G'),
        ('w', 'W'),
        ('wf', 'WF'),
        ('nr', 'NR'),
        ('r', 'R'),
        ('i', 'I'),
        ('e', 'E'),
        ('ca', 'CA'),
        ('cr', 'CR'),
        ('rc', 'RC'),
    ])

    student_plan_item_id = fields.Many2one(comodel_name='sisi.student.plan.item',
                                           readonly=True, )
