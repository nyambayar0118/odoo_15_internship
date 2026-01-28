from odoo import api, fields, models


class TeacherWizard(models.TransientModel):
    _name = 'teacher.wizard'
    _description = 'Teacher Wizard for adding students'

    teacher_id = fields.Many2one(
        'demo_school.teacher',
        string='Teacher',
        required=True,
        help='Teacher whom the students will be assigned'
    )

    student_ids = fields.Many2many(
        'demo_school.student',
        string='Students',
    )

    total_student_count = fields.Integer(
        string='Total Student Count',
        compute='_total_student_count'
    )

    student_count = fields.Integer(
        string='Selected',
        compute='_compute_student_count'
    )

    @api.depends('teacher_id')
    def _compute_student_ids(self):
        for wizard in self:
            if wizard.teacher_id:
                students = self.env['demo_school.student'].search([
                    '|',
                    ('teacher_id', '=', False),
                    ('teacher_id', '!=', wizard.teacher_id.id),
                ])
            else:
                students = self.env['demo_school.student'].search([])

            wizard.student_ids = students

    def action_add_students(self):
        self.ensure_one()
        for student in self.student_ids:
            student.teacher_id = self.teacher_id
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('student_ids')
    def _compute_student_count(self):
        for wizard in self:
            selected = len(wizard.student_ids)

            wizard.student_count = (float(
                wizard.total_student_count - selected) / wizard.total_student_count * 100) if wizard.total_student_count else 0

    @api.depends('student_ids')
    def _total_student_count(self):
        obj = self.env['demo_school.student']
        # for i in range(20):
        #     print(obj.search_count([]))
        for data in self:
            data.total_student_count = obj.search_count([])
