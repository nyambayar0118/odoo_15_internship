from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta


class Bonus(models.Model):
    _name = "owallet.bonus"
    _description = "Owallet Bonus"
    _order = "year desc, month desc"
    _rec_name = "display_name"

    year = fields.Integer(
        string='Year',
        required=True,
        default=lambda self: datetime.now().year,
    )

    month = fields.Integer(
        string='Month',
        required=True,
        default=lambda self: datetime.now().month,
    )

    amount = fields.Monetary(
        string='Bonus Amount',
        default=0.0,
        currency_field='currency_id',
        readonly=True,
        compute='_compute_amount',
        store=True,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    sent = fields.Boolean(
        string='Bonus Sent',
        default=False,
        readonly=True,
    )

    teacher_id = fields.Many2one(
        comodel_name="res.users",
        string='Teacher',
        required=True,
    )

    transaction_id = fields.Many2one(
        comodel_name="owallet.transaction",
        string='Bonus Transaction',
        readonly=True,
    )

    bonus_percentage = fields.Float(
        string='Bonus Percentage',
        default=70.0,
        help='Percentage of course payments that goes to teacher bonus'
    )

    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('sent', 'Sent'),
    ], default='draft', string='Status')

    _sql_constraints = [(
        'unique_bonus_per_month',
        'UNIQUE(year, month, teacher_id)',
        'Teacher can only have one bonus record per month'
    )]

    bonus_date = fields.Datetime(
        string='Bonus Date',
        comupte='_compute_bonus_date',
        store=False
    )

    @api.depends('year', 'month')
    def _compute_bonus_date(self):
        for record in self:
            if record.year and record.month:
                record.bonus_date = datetime(record.year, record.month, 1).date()
            elif record.year:
                record.bonus_date = datetime(record.year, 1, 1).date()
            else:
                record.bonus_date = False

    @api.depends('teacher_id', 'month', 'year')
    def _compute_display_name(self):
        for record in self:
            if record.teacher_id:
                record.display_name = f'{record.teacher_id.name} - {record.month}/{record.year}'
            else:
                record.display_name = f'{record.month}/{record.year}'

    @api.depends('teacher_id', 'year', 'month', 'bonus_percentage')
    def _compute_amount(self):
        for record in self:
            if not record.teacher_id:
                record.amount = 0.0
                continue

            first_day = datetime(record.year, record.month, 1)
            if record.month == 12:
                last_day = datetime(record.year + 1, 1, 1) - timedelta(seconds=1)
            else:
                last_day = datetime(record.year, record.month + 1, 1) - timedelta(seconds=1)

            teacher_courses = self.env['olearn2.course'].sudo().search([
                ('teacher_id', '=', record.teacher_id.id)
            ])

            transactions = self.env['owallet.transaction'].search([
                ('course_id', 'in', teacher_courses.ids),
                ('type', '=', 'expenditure'),
                ('date', '>=', first_day),
                ('date', '<=', last_day),
            ])

            total_payments = sum(transactions.mapped('amount'))

            record.amount = total_payments * (record.bonus_percentage / 100.0)

    def action_calculate_bonus(self):
        self.ensure_one()

        if not self.env.user.has_group('owallet.group_accountant'):
            raise exceptions.AccessError("Only accountants can calculate bonuses")

        self._compute_amount()
        self.write({'state': 'calculated'})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bonus Calculated',
                'message': f'Bonus amount: {self.amount} {self.currency_id.symbol}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_send_bonus(self):
        self.ensure_one()

        if not self.env.user.has_group('owallet.group_accountant'):
            raise exceptions.AccessError("Only accountants can send bonuses")

        if self.sent:
            raise exceptions.UserError("Bonus has already been sent")

        if self.amount <= 0:
            raise exceptions.UserError("Bonus amount must be greater than 0")

        transaction = self.env['owallet.transaction'].create_bonus_transaction(
            teacher_user=self.teacher_id,
            amount=self.amount,
            bonus_record=self,
            description=f'Bonus for {self.month}/{self.year}'
        )

        self.write({
            'transaction_id': transaction.id,
            'sent': True,
            'state': 'sent',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bonus Sent',
                'message': f'Bonus of {self.amount} {self.currency_id.symbol} sent to {self.teacher_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def action_calculate_all_bonuses(self):
        if not self.env.user.has_group('owallet.group_accountant'):
            raise exceptions.AccessError("Only accountants can calculate bonuses")

        now = datetime.now()
        current_year = now.year
        current_month = now.month

        master_balance_users = self.env['owallet.balance'].sudo().search([
            ('is_master', '=', True)
        ]).mapped('owner_id')

        teachers = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('olearn2.group_teacher').id]),
            ('id', 'not in', master_balance_users.ids),
        ])

        created_count = 0
        for teacher in teachers:
            existing_bonus = self.search([
                ('teacher_id', '=', teacher.id),
                ('year', '=', current_year),
                ('month', '=', current_month),
            ], limit=1)

            if not existing_bonus:
                self.create({
                    'teacher_id': teacher.id,
                    'year': current_year,
                    'month': current_month,
                })
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Bonuses Calculated',
                'message': f'{created_count} bonus records created/updated',
                'type': 'success',
                'sticky': False,
            }
        }
