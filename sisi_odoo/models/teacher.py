from odoo import models, fields
from . import employee


class Teacher(models.Model):
    _name = "sisi.teacher"
    _description = "Teacher Definition & Management"
    _inherits = {"sisi.employee": "employee_id"}

    employee_id = fields.Many2one(
        "sisi.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )
    specialization = fields.Text(string="Subject Specialization", required=True)

    def name_get(self):
        result = []
        for teacher in self:
            display_name = f"{teacher.last_name[0]}.{teacher.first_name}"
            result.append((teacher.id, display_name))
        return result
