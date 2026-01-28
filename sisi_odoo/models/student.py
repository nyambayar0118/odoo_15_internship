from odoo import fields, models, api


class Student(models.Model):
    _name = "sisi.student"
    _description = "Student Definition & Management"
    _inherits = {'sisi.user': 'user_id'}

    user_id = fields.Many2one(
        "sisi.user",
        string="User",
        required=True,
        ondelete="cascade",
    )
    enrollment_year = fields.Integer(string="Enrollment Year", required=True)
    sisi_id = fields.Char(string="SISI ID")

    major_program_id = fields.Many2one(comodel_name='sisi.program',
                                       string="Major Program",
                                       ondelete="cascade",
                                       required=False)
    minor_program_id = fields.Many2one(comodel_name='sisi.program',
                                       string="Minor Program",
                                       ondelete="cascade",
                                       required=False,
                                       domain=lambda self: [('id', '!=', self.major_program_id.id)]
                                       )

    @api.onchange('major_program_id')
    def _change_minor_list(self):
        if self.major_program_id:
            return {'domain': {
                'minor_program_id': [('id', '!=', self.major_program_id.id)]
            }}
        else:
            return {'domain': {'minor_program_id': []}}

    _sql_constraints = [
        (
            "major_minor_different",
            "CHECK(major_program_id != minor_program_id)",
            "Student's major and minor programs must be different"
        ),
        (
            "unique_sisi_id",
            "UNIQUE(sisi_id)",
            "Each student's sisi id must be unique"
        )
    ]

    def name_get(self):
        result = []
        for student in self:
            display_name = f"{student.last_name[0]}.{student.first_name}"
            result.append((student.id, display_name))
        return result
