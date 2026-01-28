from odoo import models, fields


class Attendance(models.Model):
    _name = 'sisi.attendance'
    _description = 'Attendance Management'

    attendance_date = fields.Date(string='Attendance Date', required=True)
    attendance_type = fields.Selection([
        ('lecture', 'Lecture'),
        ('seminar', 'seminar'),
        ('laboratory', 'laboratory'),
    ])
