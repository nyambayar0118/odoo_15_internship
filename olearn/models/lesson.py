from odoo import fields, models, api


class Lesson(models.Model):
    _name = "olearn.lesson"
    _description = "Lesson Records"
    _order = "lesson_template_id, student_id"
    _rec_name = "lesson_template_id"

    # -------------- BASIC FIELDS --------------
    is_viewed = fields.Boolean(
        string="Viewed",
        default=False,
        help="Mark as viewed when student completes the lesson"
    )
    viewed_date = fields.Datetime(
        string="Viewed Date",
        readonly=True,
        copy=False
    )

    # -------------- TEMPLATE FIELDS (Related) --------------
    template_link = fields.Text(
        string="Link",
        related="lesson_template_id.link",
        readonly=True
    )
    template_type = fields.Selection(
        string="Type",
        related="lesson_template_id.type",
        readonly=True
    )
    template_content = fields.Text(
        string="Content",
        related="lesson_template_id.content",
        readonly=True
    )
    template_name = fields.Char(
        string="Lesson Name",
        related="lesson_template_id.name",
        readonly=True,
        store=True
    )

    # -------------- RELATIONS --------------
    lesson_template_id = fields.Many2one(
        comodel_name="olearn.lesson.template",
        string="Lesson Template",
        required=True,
        ondelete="cascade",
        index=True
    )
    student_id = fields.Many2one(
        comodel_name="res.users",
        string="Student",
        required=True,
        ondelete="cascade",
        index=True
    )
    program_id = fields.Many2one(
        string="Program",
        related="lesson_template_id.program_id",
        store=True,
        readonly=True
    )

    _sql_constraints = [
        ('unique_lesson_student',
         'UNIQUE(lesson_template_id, student_id)',
         'A student can only have one record per lesson template!')
    ]

    # Mark lesson as viewed
    def action_mark_viewed(self):
        self.write({
            'is_viewed': True,
            'viewed_date': fields.Datetime.now()
        })

    # Prevent duplicate lessons for same student
    @api.model
    def create(self, vals):
        if 'lesson_template_id' in vals and 'student_id' in vals:
            existing = self.search([
                ('lesson_template_id', '=', vals['lesson_template_id']),
                ('student_id', '=', vals['student_id'])
            ], limit=1)
            if existing:
                return existing
        return super().create(vals)
