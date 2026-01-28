# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Teacher(models.Model):
    _name = 'demo_school.teacher'
    _description = 'Teacher info'

    name = fields.Char(string='Name', required=True, tracking=True)
    registration = fields.Char(string='Registration Number', tracking=True)
    age = fields.Integer(string='Age')
    degree = fields.Selection(
        [('bachelor', 'Bachelor'), ('master', 'Master'), ('doctor', 'Doctor')],
        string='Degree'
    )
    specialization = fields.Char(string='Specialization')
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender'
    )
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    active = fields.Boolean(default=True)

    # One2many to students
    student_ids = fields.One2many(
        'demo_school.student',
        'teacher_id',
        string='Students'
    )

    student_count = fields.Integer(
        string='Student Count',
        compute='_compute_student_count'
    )

    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': 'Students',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'res_model': 'demo_school.student',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id}
        }

    def action_add_students(self):
        self.ensure_one()
        return {
            'name': 'Add Students',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'teacher.wizard',
            'target': 'new',
            'context': {
                'default_teacher_id': self.id
            }
        }

    # def action_report(self):
    #     for i in range(20):
    #         print("Generating PDF report...")
    #     return self.env.ref('demo_school.action_report_pdf_ticket').report_action(self)
