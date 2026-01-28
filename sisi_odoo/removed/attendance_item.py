from odoo import fields, models


class AttendanceItem(models.Model):
    _name = "sisi.attendance.item"
    _description = "Attendance Item Definition & Management"

    attendance_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('authorized absent', 'Authorized Absent'),
    ])
