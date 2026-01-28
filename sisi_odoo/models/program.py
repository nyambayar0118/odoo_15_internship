from odoo import fields, models


class Program(models.Model):
    _name = "sisi.program"
    _description = "Program Definition & Management"

    index = fields.Char(string="Index", required=True)
    name = fields.Char(string="Program Name", required=True)
    created_year = fields.Integer(string="Created Year", required=True)
    type = fields.Selection([("bachelor", "Bachelor"),
                             ("master", "Master"),
                             ("doctor", "Doctor")])

    duration_years = fields.Integer(string="Duration (Years)", required=True, default=4)
    description = fields.Text(string="Program Description")

    school_id = fields.Many2one(comodel_name="sisi.school")
    department_id = fields.Many2one(comodel_name="sisi.department")

    def name_get(self):
        result = []
        for program in self:
            display_name = f"{program.name} ({program.created_year})"
            result.append((program.id, display_name))
        return result
