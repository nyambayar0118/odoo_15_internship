from odoo import fields, models, api, exceptions


class Program(models.Model):
    _name = "olearn.program"
    _description = "Programmes available on oLearn"
    _order = "name"

    # -------------- BASIC FIELDS --------------
    name = fields.Char(required=True, index=True)
    description = fields.Text(required=True, default="Not Set")
    active = fields.Boolean(default=True, help="Archive inactive programs")

    status = fields.Boolean(
        string="Is the student in this class?",
        store=False,
        compute="_compute_status"
    )

    # -------------- RELATIONS --------------
    teacher_id = fields.Many2many(
        "res.users",
        "program_teacher_rel",
        "program_id",
        "user_id",
        string="Teachers",
        required=True,
        groups="olearn.group_manager",
        default=lambda self: [(4, self.env.user.id)],
        domain=lambda self: [("groups_id", "in", [self.env.ref("olearn.group_teacher").id])],
    )

    student_ids = fields.Many2many(
        "res.users",
        "program_student_rel",
        "program_id",
        "user_id",
        string="Students",
        domain=lambda self: [("groups_id", "in", [self.env.ref("olearn.group_student").id])],
    )

    lesson_template_ids = fields.One2many(
        "olearn.lesson.template",
        "program_id",
        string="Lesson Templates"
    )

    task_template_ids = fields.One2many(
        "olearn.task.template",
        "program_id",
        string="Task Templates"
    )

    # -------------- COMPUTED FIELDS --------------
    lesson_count = fields.Integer(
        string="Lesson Count",
        compute="_compute_lesson_count",
        store=True
    )

    student_count = fields.Integer(
        string="Student Count",
        compute="_compute_student_count",
        store=True
    )

    def join_program(self):
        """Automatically creates lessons and tasks for is-hidden=false templates"""
        for program in self:
            current_user = self.env.user

            if not current_user.has_group('olearn.group_student'):
                raise exceptions.UserError(
                    "Only students can join programs. "
                    "Please contact your administrator to be assigned the student role."
                )

            if current_user.id in program.student_ids.ids:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Already Joined',
                        'message': 'You are already enrolled in this program.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }

            # Add student to program
            program.sudo().write({"student_ids": [(4, current_user.id)]})

            # Get only is_hidden=False templates
            visible_lessons = program.sudo().lesson_template_ids.filtered(
                lambda l: not l.is_hidden
            )
            visible_tasks = program.sudo().task_template_ids.filtered(
                lambda t: not t.is_hidden
            )

            # Create lesson records
            lesson_vals = [{
                'lesson_template_id': lesson.id,
                'student_id': current_user.id,
                'is_viewed': False
            } for lesson in visible_lessons]
            if lesson_vals:
                self.env["olearn.lesson"].sudo().create(lesson_vals)

            # Create task records
            task_vals = [{
                'task_template_id': task.id,
                'student_id': current_user.id,
                'score': 0,
                'status': 'assigned',
                'is_submittable': True
            } for task in visible_tasks]
            if task_vals:
                self.env["olearn.task"].sudo().create(task_vals)

            # Show notification to user
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': f'You have joined {program.name}. {len(lesson_vals)} lessons and {len(task_vals)} tasks assigned.',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_view_lessons(self):
        self.ensure_one()
        return {
            'name': f'Lessons - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'olearn.lesson.template',
            'view_mode': 'tree,form',
            'domain': [('program_id', '=', self.id)],
            'context': {'default_program_id': self.id},
        }

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': f'Students - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.student_ids.ids)],
            'context': {'default_groups_id': [(4, self.env.ref('olearn.group_student').id)]},
        }

    # Check if current user is enrolled in this program
    @api.depends("student_ids")
    def _compute_status(self):
        current_user = self.env.user.id
        for program in self:
            program.status = current_user in program.student_ids.ids

    # Compute lesson templates count in program
    @api.depends("lesson_template_ids")
    def _compute_lesson_count(self):
        for program in self:
            program.lesson_count = len(program.lesson_template_ids)

    # Compute enrolled students count
    @api.depends("student_ids")
    def _compute_student_count(self):
        for program in self:
            program.student_count = len(program.student_ids)
