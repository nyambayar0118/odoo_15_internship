from odoo import fields, models, api
from datetime import datetime, timedelta, time


class Task(models.Model):
    _name = "olearn2.task"
    _description = "Task"
    _order = "course_id, due_date, name"

    # -------------- BASIC FIELDS --------------
    name = fields.Char(
        string="Task Name",
        required=True,
        index=True
    )
    type = fields.Selection(
        [
            ("problem", "Problem"),
            ("writing", "Writing"),
            ("quiz", "Quiz"),
            ("project", "Project"),
            ("other", "Other"),
        ],
        string="Task Type",
        required=True,
        default="problem"
    )
    content = fields.Html(
        string="Task Content",
        help="Detailed task description and instructions"
    )
    due_date = fields.Datetime(
        string="Due Date",
        default=lambda self: datetime.combine(
            datetime.today().date() + timedelta(days=7),
            time(23, 59)
        )
    )
    max_score = fields.Integer(
        string="Max Score",
        default=10,
        required=True
    )
    hidden = fields.Boolean(
        string="Hidden from students",
        default=True,
        help="When unchecked, task will be automatically assigned to all enrolled students"
    )
    active = fields.Boolean(default=True)

    # -------------- RELATIONS --------------
    course_id = fields.Many2one(
        comodel_name='olearn2.course',
        domain=lambda self: [('teacher_id', '=', self.env.user.id)],
        string="Program",
        required=True,
        store=True,
        ondelete="cascade",
        index=True
    )
    lesson_id = fields.Many2one(
        comodel_name="olearn2.lesson",
        domain="[('course_id', '=', course_id)]",
        string="Related Lesson",
        help="Optional: Link task to a specific lesson"
    )

    task_record_ids = fields.One2many(
        "olearn2.task.record",
        "task_id",
        string="Student Task records"
    )

    # -------------- COMPUTED FIELDS --------------
    assigned_count = fields.Integer(
        string="Students Assigned",
        compute="_compute_assigned_count",
        store=False
    )

    # Count students who have this task
    @api.depends('task_record_ids')
    def _compute_assigned_count(self):
        for task in self:
            task.assigned_count = len(task.task_record_ids)

    completed_count = fields.Integer(
        string="Students Completed",
        compute="_compute_completed_count",
        store=False
    )

    # Count students who have this task
    @api.depends('task_record_ids')
    def _compute_completed_count(self):
        for task in self:
            task.completed_count = len(
                task.task_record_ids.filtered(
                    lambda r: r.status == 'graded'
                )
            )

    # Publish task to students
    def action_publish_to_students(self):
        self.write({'hidden': False})
        return True

    # Hide task from students
    def action_hide_from_students(self):
        self.write({'hidden': True})
        return True

    # When creating a task template, assign to enrolled students if is_hidden=False
    @api.model
    def create(self, vals):
        task = super().create(vals)

        if not task.hidden and task.course_id:
            task._create_task_records_for_students()

        return task

    # When unhiding a task template, create tasks for all students
    def write(self, vals):
        result = super().write(vals)

        if 'hidden' in vals and not vals['hidden']:
            for task in self:
                task._create_task_records_for_students()

        return result

    # Create task records for all enrolled students who don't have it yet
    def _create_task_records_for_students(self):
        self.ensure_one()

        if not self.course_id or not self.course_id.student_ids:
            return

        existing_student_ids = self.task_record_ids.mapped('student_id').ids
        students_to_add = self.course_id.student_ids.filtered(
            lambda s: s.id not in existing_student_ids
        )

        task_record_vals = [{
            'task_id': self.id,
            'student_id': student.id,
            'score': 0,
            'status': 'assigned',
            'submittable': True
        } for student in students_to_add]

        if task_record_vals:
            self.env["olearn2.task.record"].sudo().create(task_record_vals)

    # Clear lesson template when program changes and update domain
    @api.onchange('course_id')
    def _onchange_course_id(self):
        self.lesson_id = False

        if self.course_id:
            return {
                'domain': {
                    'lesson_id': [
                        ('course_id', '=', self.course_id.id)
                    ]
                }
            }
        else:
            return {
                'domain': {
                    'lesson_id': []
                }
            }
