from odoo import fields, models, api


class LessonRecord(models.Model):
    _name = "olearn2.lesson.record"
    _description = "Lesson Records"
    _order = "lesson_id, student_id"
    _rec_name = "lesson_id"

    # -------------- BASIC FIELDS --------------
    viewed = fields.Boolean(
        string="Viewed",
        default=False,
        help="Mark as viewed when student completes the lesson"
    )
    viewed_date = fields.Datetime(
        string="Viewed Date",
        readonly=True,
        copy=False
    )

    # -------------- RELATIONS --------------
    lesson_id = fields.Many2one(
        comodel_name="olearn2.lesson",
        string="Lesson",
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

    # -------------- TEMPLATE FIELDS (Related) --------------
    lesson_link = fields.Text(
        string="Link",
        related="lesson_id.link",
        readonly=True,
        store=False
    )
    lesson_type = fields.Selection(
        string="Type",
        related="lesson_id.type",
        readonly=True,
        store=False
    )
    lesson_content = fields.Text(
        string="Content",
        related="lesson_id.content",
        readonly=True,
        store=False
    )

    _sql_constraints = [
        ('unique_lesson_student',
         'UNIQUE(lesson_id, student_id)',
         'A student can only have one record per lesson!')
    ]

    # Mark lesson as viewed
    def action_mark_viewed(self):
        self.write({
            'viewed': True,
            'viewed_date': fields.Datetime.now()
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # Prevent duplicate lessons for same student
    @api.model
    def create(self, vals):
        if 'lesson_id' in vals and 'student_id' in vals:
            existing = self.search([
                ('lesson_id', '=', vals['lesson_id']),
                ('student_id', '=', vals['student_id'])
            ], limit=1)
            if existing:
                return existing
        return super().create(vals)
