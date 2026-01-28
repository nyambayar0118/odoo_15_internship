from odoo import fields, models, api


class LessonTemplate(models.Model):
    _name = "olearn.lesson.template"
    _description = "Lesson Template"
    _order = "program_id, sequence, name"

    # -------------- BASIC FIELDS --------------
    name = fields.Char(
        string="Lesson Template Name",
        required=True,
        index=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Order of lessons in the program"
    )
    content = fields.Text(
        string="Content",
        required=True
    )
    link = fields.Text(
        string="Link to content",
        help="URL or path to lesson materials"
    )
    is_hidden = fields.Boolean(
        string="Hidden from students",
        default=True,
        help="When unchecked, lesson will be automatically assigned to all enrolled students"
    )
    type = fields.Selection(
        [
            ("video", "Video"),
            ("example", "Example"),
            ("material", "Material"),
            ("reading", "Reading"),
        ],
        string="Lesson Type",
        required=True,
        default="material"
    )
    active = fields.Boolean(default=True)

    # -------------- RELATIONS --------------
    teacher_id = fields.Many2many(
        comodel_name="res.users",
        relation="lesson_template_teacher_rel",
        column1="lesson_template_id",
        column2="user_id",
        default=lambda self: [(6, 0, [self.env.user.id])],
        string="Teacher",
        readonly=True,
        store=True
    )
    program_id = fields.Many2one(
        comodel_name="olearn.program",
        domain=lambda self: [('teacher_id', 'in', self.env.user.ids)],
        string="Program",
        required=True,
        ondelete="cascade",
        index=True
    )

    lesson_ids = fields.One2many(
        "olearn.lesson",
        "lesson_template_id",
        string="Student Lessons"
    )

    # -------------- COMPUTED FIELDS --------------
    student_count = fields.Integer(
        string="Students Assigned",
        compute="_compute_student_count",
        store=True
    )

    task_template_ids = fields.One2many(
        "olearn.task.template",
        "lesson_template_id",
        string="Task Templates",
    )

    task_template_count = fields.Integer(
        string="Task Templates Assigned",
        compute="_compute_task_template_count",
        store=True
    )

    # Compute students who have this lesson
    @api.depends('lesson_ids')
    def _compute_student_count(self):
        for template in self:
            template.student_count = len(template.lesson_ids)

    # Compute task template count when tasl_template_ids changes
    @api.depends('task_template_ids')
    def _compute_task_template_count(self):
        for template in self:
            template.task_template_count = len(template.task_template_ids)

    # Publish lesson to students LOGIC
    def action_publish_to_students(self):
        self.write({'is_hidden': False})
        return True

    def action_hide_from_students(self):
        self.write({'is_hidden': True})
        return True

    # When creating a lesson template, assign to enrolled students if is_hidden=False
    @api.model
    def create(self, vals):
        template = super().create(vals)

        if not template.is_hidden and template.program_id:
            template._create_lessons_for_students()
        return template

    # When unhiding a lesson template, create lessons record for all students
    def write(self, vals):
        result = super().write(vals)

        # Check if is_hidden was changed from True to False
        if 'is_hidden' in vals and not vals['is_hidden']:
            for template in self:
                template._create_lessons_for_students()

        return result

    # Create lesson records for all students who don't have it
    def _create_lessons_for_students(self):
        self.ensure_one()

        if not self.program_id or not self.program_id.student_ids:
            return

        existing_student_ids = self.lesson_ids.mapped('student_id').ids
        students_to_add = self.program_id.student_ids.filtered(
            lambda s: s.id not in existing_student_ids
        )

        lesson_vals = [{
            'lesson_template_id': self.id,
            'student_id': student.id,
            'is_viewed': False
        } for student in students_to_add]

        if lesson_vals:
            self.env["olearn.lesson"].sudo().create(lesson_vals)
