from odoo import fields, models, api


class Lesson(models.Model):
    _name = "olearn2.lesson"
    _description = "Lesson model"
    _order = "course_id, sequence, name"

    # -------------- BASIC FIELDS --------------
    name = fields.Char(
        string="Lesson Name",
        required=True,
        index=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=1,
        help="Order of lessons in the course"
    )
    content = fields.Text(
        string="Content",
        required=True
    )
    link = fields.Text(
        string="Link to content",
        help="URL or path to lesson materials"
    )
    hidden = fields.Boolean(
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
            ("other", "Other"),
        ],
        string="Lesson Type",
        required=True,
        default="material"
    )

    task_count = fields.Integer(
        string="Task Count for this lesson",
        compute="_compute_task_count",
        store=True
    )

    # Compute task template count when tasl_template_ids changes
    @api.depends('task_ids')
    def _compute_task_count(self):
        for task in self:
            task.task_count = len(task.task_ids)

    # -------------- RELATIONS --------------
    course_id = fields.Many2one(
        comodel_name="olearn2.course",
        domain=lambda self: [('teacher_id', '=', self.env.user.id)],
        string="Course",
        required=True,
        ondelete="cascade",
        index=True
    )

    lesson_record_ids = fields.One2many(
        "olearn2.lesson.record",
        "lesson_id",
        string="Student Lessons"
    )

    task_ids = fields.One2many(
        "olearn2.task",
        "lesson_id",
        string="Tasks related to this lesson",
    )

    # Publish lesson to students LOGIC
    def action_publish_to_students(self):
        self.write({'hidden': False})
        return True

    def action_hide_from_students(self):
        self.write({'hidden': True})
        return True

    # When creating a lesson template, assign to enrolled students if is_hidden=False
    @api.model
    def create(self, vals):
        lesson = super().create(vals)

        if not lesson.hidden and lesson.course_id:
            lesson._create_lesson_records_for_students()
        return lesson

    # When unhiding a lesson template, create lessons record for all students
    def write(self, vals):
        result = super().write(vals)

        # Check if is_hidden was changed from True to False
        if 'hidden' in vals and not vals['hidden']:
            for lesson in self:
                lesson._create_lesson_records_for_students()

        return result

    # Create lesson records for all students who don't have it
    def _create_lesson_records_for_students(self):
        self.ensure_one()

        if not self.course_id or not self.course_id.student_ids:
            return

        existing_student_ids = self.lesson_record_ids.mapped('student_id').ids
        students_to_add = self.course_id.student_ids.filtered(
            lambda s: s.id not in existing_student_ids
        )

        lesson_record_vals = [{
            'lesson_id': self.id,
            'student_id': student.id,
            'viewed': False
        } for student in students_to_add]

        if lesson_record_vals:
            self.env["olearn2.lesson.record"].sudo().create(lesson_record_vals)
