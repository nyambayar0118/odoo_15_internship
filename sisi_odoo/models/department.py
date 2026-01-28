from odoo import fields, models, api


class Department(models.Model):
    _name = "sisi.department"
    _description = "Department Definition & Management"

    name = fields.Char(string="Department Name", required=True)

    school_id = fields.Many2one(
        comodel_name="sisi.school",
        string="School",
        required=True,
        ondelete="cascade",
    )

    room_id = fields.Many2one(
        comodel_name="sisi.room",
        string="Department Room",
        required=False,
        ondelete="set null",
    )

    _sql_constraints = [
        (
            "unique_department_name",
            "unique(name)",
            "The department name must be unique.",
        ),
        (
            "unique_department_room",
            "unique(room_id)",
            "This room is already assigned to another department.",
        ),
    ]

    @api.onchange('school_id')
    def _onchange_school_id(self):
        if self.school_id:
            return {
                'domain': {
                    'room_id': [('school_id', '=', self.school_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'room_id': []
                }
            }
