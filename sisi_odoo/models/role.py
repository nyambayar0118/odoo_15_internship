from odoo import fields, models


class Role(models.Model):
    _name = "sisi.role"
    _description = "Employee Role Definition & Management"

    name = fields.Char(string="Role Name", required=True)
    description = fields.Text(string="Role Description", required=True)

    _sql_constraints = [
        (
            "unique_role_name",
            "unique(name)",
            "The role name must be unique.",
        ),
    ]
