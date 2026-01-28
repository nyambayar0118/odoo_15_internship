from odoo import fields, models, api, exceptions


class Course(models.Model):
    _name = "olearn2.course"
    _description = "Courses available on oLearn"
    _order = "name"

    # -------------- BASIC FIELDS --------------
    name = fields.Char(required=True, index=True)
    description = fields.Text(required=True, default="Not Set")
    active = fields.Boolean(default=True, help="Archive inactive programs")

    # Check if current user is enrolled in this program
    joined = fields.Boolean(
        string="Is the student in this class?",
        store=False,
        compute="_compute_joined"
    )

    @api.depends("student_ids")
    def _compute_joined(self):
        current_user = self.env.user.id
        for course in self:
            course.joined = current_user in course.student_ids.ids

    # -------------- RELATIONS --------------
    teacher_id = fields.Many2one(
        "res.users",
        string="Teachers",
        required=True,
        groups="olearn2.group_manager",
        default=lambda self: self.env.user,
        domain=lambda self: [("groups_id", "in", [self.env.ref("olearn2.group_teacher").id])],
    )

    student_ids = fields.Many2many(
        "res.users",
        "course_student_rel",
        "course_id",
        "user_id",
        string="Students",
        domain=lambda self: [("groups_id", "in", [self.env.ref("olearn2.group_student").id])],
    )

    lesson_ids = fields.One2many(
        "olearn2.lesson",
        "course_id",
        string="Lessons for this course"
    )

    task_ids = fields.One2many(
        "olearn2.task",
        "course_id",
        string="Tasks for this course"
    )

    # -------------- COMPUTED FIELDS --------------
    lesson_count = fields.Integer(
        string="Lesson Count",
        compute="_compute_lesson_count",
        store=True
    )

    # Compute lesson templates count in program
    @api.depends("lesson_ids")
    def _compute_lesson_count(self):
        for course in self:
            course.lesson_count = len(course.lesson_ids)

    task_count = fields.Integer(
        string="Task Count",
        compute="_compute_task_count",
        store=True
    )

    @api.depends("task_ids")
    def _compute_task_count(self):
        for course in self:
            course.task_count = len(course.task_ids)

    student_count = fields.Integer(
        string="Student Count",
        compute="_compute_student_count",
        store=True
    )

    # Compute enrolled students count
    @api.depends("student_ids")
    def _compute_student_count(self):
        for course in self:
            course.student_count = len(course.student_ids)

    cost = fields.Monetary(
        string="Cost for this Course",
        currency_field="currency_id",
        required=True,
    )

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    # Replace the join_course method in course.py:

    def join_course(self):
        """Automatically creates lessons and tasks for is-hidden=false templates"""
        for course in self:
            current_user = self.env.user

            if not current_user.has_group('olearn2.group_student'):
                raise exceptions.UserError(
                    "Only students can join courses. "
                    "Please contact your administrator to be assigned the student role."
                )

            if current_user.id in course.student_ids.ids:
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

            # FIXED: Use the new transaction method
            result = self.env["owallet.transaction"].sudo().create_enrollment_transaction(
                student_user=current_user,
                course=course
            )

            if not result:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Failed',
                        'message': f'Your balance is insufficient. Required: {course.cost} {course.currency_id.symbol}',
                        'type': 'danger',
                        'sticky': False,
                    }
                }

            # Add student to program
            course.sudo().write({"student_ids": [(4, current_user.id)]})

            # Get only hidden=False templates
            visible_lessons = course.sudo().lesson_ids.filtered(
                lambda l: not l.hidden
            )
            visible_tasks = course.sudo().task_ids.filtered(
                lambda t: not t.hidden
            )

            # Create lesson records
            lesson_record_vals = [{
                'lesson_id': lesson.id,
                'student_id': current_user.id,
                'viewed': False
            } for lesson in visible_lessons]
            if lesson_record_vals:
                self.env["olearn2.lesson.record"].sudo().create(lesson_record_vals)

            # Create task records
            task_record_vals = [{
                'task_id': task.id,
                'student_id': current_user.id,
                'score': 0,
                'status': 'assigned',
                'submittable': True
            } for task in visible_tasks]
            if task_record_vals:
                self.env["olearn2.task.record"].sudo().create(task_record_vals)

            # Show notification to user
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': f'You have joined {course.name}. {len(lesson_record_vals)} lessons and {len(task_record_vals)} tasks assigned.',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_view_lessons(self):
        self.ensure_one()
        return {
            'name': f'Lessons - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'olearn2.lesson',
            'view_mode': 'tree,form',
            'domain': [('course_id', '=', self.id)],
            'context': {'default_course_id': self.id},
        }

    def action_view_students(self):
        self.ensure_one()
        return {
            'name': f'Students - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.student_ids.ids)],
            'context': {'default_groups_id': [(4, self.env.ref('olearn2.group_student').id)]},
        }
