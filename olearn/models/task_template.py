from odoo import fields, models, api
from datetime import datetime, timedelta, time


class TaskTemplate(models.Model):
    _name = "olearn.task.template"
    _description = "Task Template"
    _order = "program_id, due_date, name"

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
        default=100,
        required=True
    )
    is_hidden = fields.Boolean(
        string="Hidden from students",
        default=True,
        help="When unchecked, task will be automatically assigned to all enrolled students"
    )
    active = fields.Boolean(default=True)

    # -------------- RELATIONS --------------
    program_id = fields.Many2one(
        comodel_name='olearn.program',
        domain=lambda self: [('teacher_id', 'in', self.env.user.ids)],
        string="Program",
        required=True,
        store=True,
        ondelete="cascade",
        index=True
    )
    lesson_template_id = fields.Many2one(
        comodel_name="olearn.lesson.template",
        domain="[('program_id', '=', program_id)]",
        string="Related Lesson",
        help="Optional: Link task to a specific lesson"
    )
    teacher_id = fields.Many2many(
        comodel_name='res.users',
        relation='task_template_teacher_rel',
        column1='task_template_id',
        column2='user_id',
        string="Teacher",
        default=lambda self: [(6, 0, [self.env.user.id])],
        readonly=True,
        store=True
    )

    task_ids = fields.One2many(
        "olearn.task",
        "task_template_id",
        string="Student Tasks"
    )

    # -------------- COMPUTED FIELDS --------------
    student_count = fields.Integer(
        string="Students Assigned",
        compute="_compute_student_count",
        store=True
    )

    # Count students who have this task
    @api.depends('task_ids')
    def _compute_student_count(self):
        for template in self:
            template.student_count = len(template.task_ids)

    # Publish task to students
    def action_publish_to_students(self):
        self.write({'is_hidden': False})
        return True

    # Hide task from students
    def action_hide_from_students(self):
        self.write({'is_hidden': True})
        return True

    # When creating a task template, assign to enrolled students if is_hidden=False
    @api.model
    def create(self, vals):
        template = super().create(vals)

        if not template.is_hidden and template.program_id:
            template._create_tasks_for_students()

        return template

    # When unhiding a task template, create tasks for all students
    def write(self, vals):
        result = super().write(vals)

        if 'is_hidden' in vals and not vals['is_hidden']:
            for template in self:
                template._create_tasks_for_students()

        return result

    # Create task records for all enrolled students who don't have it yet
    def _create_tasks_for_students(self):
        self.ensure_one()

        if not self.program_id or not self.program_id.student_ids:
            return

        existing_student_ids = self.task_ids.mapped('student_id').ids
        students_to_add = self.program_id.student_ids.filtered(
            lambda s: s.id not in existing_student_ids
        )

        task_vals = [{
            'task_template_id': self.id,
            'student_id': student.id,
            'score': 0,
            'status': 'assigned',
            'is_submittable': True
        } for student in students_to_add]

        if task_vals:
            self.env["olearn.task"].sudo().create(task_vals)

    # Clear lesson template when program changes and update domain
    @api.onchange('program_id')
    def _onchange_program_id(self):
        self.lesson_template_id = False

        if self.program_id:
            return {
                'domain': {
                    'lesson_template_id': [
                        ('program_id', '=', self.program_id.id)
                    ]
                }
            }
        else:
            return {
                'domain': {
                    'lesson_template_id': []
                }
            }
