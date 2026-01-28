from odoo import fields, models
from . import user


class Employee(models.Model):
    _name = "sisi.employee"
    _description = "Employee Definition & Management"
    _inherits = {"sisi.user": "user_id"}

    user_id = fields.Many2one(
        "sisi.user",
        string="User",
        required=True,
        ondelete="cascade",
    )

    hire_date = fields.Date(string="Hire Date",
                            required=True,
                            default=fields.Date.today, )
    education = fields.Selection([("none", "None"),
                                  ("basic", "Basic"),
                                  ("bachelor", "Bachelor"),
                                  ("master", "Master"),
                                  ("doctor", "Doctor"), ],
                                 default="none", )
    roles = fields.Many2many(
        "sisi.role",
        string="Roles",
    )
