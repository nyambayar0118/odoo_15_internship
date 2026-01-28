from odoo import api, fields, models, exceptions


class TaskRecord(models.Model):
    _name = "olearn2.task.record"
    _description = "Task Records"
    _order = "task_id, student_id"
    _rec_name = "task_id"

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
    teacher_note = fields.Text(
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
    submittable = fields.Boolean(
        string="Can Submit",
        default=True,
        help="Enable/disable submission for this task"
    )

    # -------------- TEMPLATE FIELDS (Related) --------------
    task_name = fields.Char(
        string="Task Name",
        related="task_id.name",
        readonly=True,
        store=False
    )
    task_content = fields.Html(
        string="Instructions",
        related="task_id.content",
        readonly=True,
        store=False
    )
    task_due_date = fields.Datetime(
        string="Due Date",
        related="task_id.due_date",
        readonly=True,
        store=False
    )
    task_max_score = fields.Integer(
        string="Max Score",
        related="task_id.max_score",
        readonly=True,
        store=False
    )

    # -------------- RELATIONS --------------
    task_id = fields.Many2one(
        comodel_name="olearn2.task",
        string="Task",
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

    # -------------- COMPUTED FIELDS --------------
    overdue = fields.Boolean(
        string="Overdue",
        compute="_compute_overdue",
        store=True
    )

    _sql_constraints = [
        ('unique_task_student',
         'UNIQUE(task_id, student_id)',
         'A student can only have one record per task!'),
        ('check_score',
         'CHECK(score >= 0)',
         'Score cannot be negative!')
    ]

    # Check if task is overdue
    @api.depends('status', 'task_id.due_date')
    def _compute_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            record.overdue = (
                    record.task_id.due_date and
                    record.task_id.due_date < now and
                    record.status == 'assigned'
            )

    # Action for student submits the task
    def action_submit(self):
        self.ensure_one()

        if not self.submittable:
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
            'res_model': 'olearn2.task',
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
        if 'task_id' in vals and 'student_id' in vals:
            existing = self.search([
                ('task_id', '=', vals['task_id']),
                ('student_id', '=', vals['student_id'])
            ], limit=1)
            if existing:
                return existing
        return super().create(vals)

    # Check score doesn't exceed max score
    @api.constrains('score', 'task_id.max_score')
    def _check_score(self):
        for record in self:
            if record.task_id.max_score and record.score > record.task_id.max_score:
                raise exceptions.ValidationError(
                    f"Score ({record.score}) cannot exceed maximum score ({record.task_id.max_score})!"
                )
