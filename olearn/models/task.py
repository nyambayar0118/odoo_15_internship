from odoo import api, fields, models, exceptions


class Task(models.Model):
    _name = "olearn.task"
    _description = "Task Record"
    _order = "task_template_id, student_id"
    _rec_name = "task_template_id"

    # -------------- BASIC FIELDS --------------
    score = fields.Integer(
        string="Student's Score",
        default=0
    )
    attachment = fields.Binary(
        string="Submission Attachment",
        attachment=True
    )
    attachment_name = fields.Char(string="Attachment Name")

    submission_text = fields.Html(
        string="Submission Text",
        help="Student's text submission"
    )
    submission_date = fields.Datetime(
        string="Submission Date",
        readonly=True,
        copy=False
    )
    graded_date = fields.Datetime(
        string="Graded Date",
        readonly=True,
        copy=False
    )
    teacher_notes = fields.Text(
        string="Teacher Feedback",
        help="Teacher's comments on the submission"
    )

    status = fields.Selection(
        [
            ("assigned", "Assigned"),
            ("submitted", "Submitted"),
            ("graded", "Graded"),
            ("returned", "Returned"),
        ],
        default="assigned",
        required=True,
        index=True
    )
    is_submittable = fields.Boolean(
        string="Can Submit",
        default=True,
        help="Enable/disable submission for this task"
    )

    # -------------- TEMPLATE FIELDS (Related) --------------
    template_name = fields.Char(
        string="Task Name",
        related="task_template_id.name",
        readonly=True,
        store=True
    )
    template_content = fields.Html(
        string="Instructions",
        related="task_template_id.content",
        readonly=True
    )
    template_due_date = fields.Datetime(
        string="Due Date",
        related="task_template_id.due_date",
        readonly=True,
        store=True
    )
    template_max_score = fields.Integer(
        string="Max Score",
        related="task_template_id.max_score",
        readonly=True,
        store=True
    )

    # -------------- RELATIONS --------------
    task_template_id = fields.Many2one(
        comodel_name="olearn.task.template",
        string="Task Template",
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
        related="task_template_id.program_id",
        store=True,
        readonly=True
    )

    # -------------- COMPUTED FIELDS --------------
    is_overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_is_overdue",
        store=True
    )

    _sql_constraints = [
        ('unique_task_student',
         'UNIQUE(task_template_id, student_id)',
         'A student can only have one record per task template!'),
        ('check_score',
         'CHECK(score >= 0)',
         'Score cannot be negative!')
    ]

    # Check if task is overdue
    @api.depends('template_due_date', 'status')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for task in self:
            task.is_overdue = (
                    task.template_due_date and
                    task.template_due_date < now and
                    task.status == 'assigned'
            )

    # Action for student submits the task
    def action_submit(self):
        self.ensure_one()

        if not self.is_submittable:
            raise exceptions.UserError("This task is not submittable.")

        if self.status not in ['assigned', 'returned']:
            raise exceptions.UserError("Task has already been submitted.")

        self.write({
            'status': 'submitted',
            'submission_date': fields.Datetime.now()
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Submitted!',
                'message': 'Your task has been submitted successfully.',
                'type': 'success',
                'sticky': False,
            }
        }

    # Action for teacher grades the task
    def action_grade(self):
        self.ensure_one()

        if self.status != 'submitted':
            raise exceptions.UserError("Task must be submitted before grading.")

        return {
            'name': 'Grade Task',
            'type': 'ir.actions.act_window',
            'res_model': 'olearn.task',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'grading_mode': True}
        }

    # Action for teacher returns graded task to student
    def action_return_to_student(self):
        for task in self:
            if task.status != 'submitted':
                continue

            task.write({
                'status': 'returned',
                'graded_date': fields.Datetime.now()
            })

    def action_mark_as_done(self):
        for task in self:
            if task.status != 'submitted':
                continue

            task.write({
                'status': 'graded',
                'graded_date': fields.Datetime.now()
            })

    # Prevent duplicate tasks for same student
    @api.model
    def create(self, vals):
        if 'task_template_id' in vals and 'student_id' in vals:
            existing = self.search([
                ('task_template_id', '=', vals['task_template_id']),
                ('student_id', '=', vals['student_id'])
            ], limit=1)
            if existing:
                return existing
        return super().create(vals)

    # Check score doesn't exceed max score
    @api.constrains('score', 'template_max_score')
    def _check_score(self):
        for task in self:
            if task.template_max_score and task.score > task.template_max_score:
                raise exceptions.ValidationError(
                    f"Score ({task.score}) cannot exceed maximum score ({task.template_max_score})!"
                )
