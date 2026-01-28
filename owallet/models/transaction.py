from odoo import fields, models, api, exceptions


class Transaction(models.Model):
    _name = "owallet.transaction"
    _description = "Owallet Transaction"
    _order = "date desc"
    _rec_name = "description"

    balance_id = fields.Many2one(
        comodel_name='owallet.balance',
        string='Balance',
        required=True,
        ondelete='cascade',
        index=True,
    )

    owner_id = fields.Many2one(
        related='balance_id.owner_id',
        string='Owner',
        store=True,
        readonly=True,
    )

    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    type = fields.Selection([
        ("deposit", "Deposit"),
        ("expenditure", "Expenditure"),
        ("withdraw", "Withdraw"),
        ("bonus", "Bonus Payout"),
    ],
        string='Transaction Type',
        required=True,
    )

    source = fields.Selection([
        ("automatic", "Automatic"),
        ("accountant", "Accountant"),
    ],
        string='Source',
        required=True,
    )

    course_id = fields.Many2one(
        comodel_name='olearn2.course',
        string='Related Course',
    )

    description = fields.Char(
        string='Description',
        required=True,
    )

    date = fields.Datetime(
        string='Transaction Date',
        default=fields.Datetime.now,
        required=True,
    )

    bonus_id = fields.Many2one(
        'owallet.bonus',
        string='Related Bonus',
    )

    @api.model
    def create(self, vals):
        transaction = super().create(vals)

        balance = transaction.balance_id

        if transaction.type == 'deposit' or transaction.type == 'bonus':
            balance.add_funds(transaction.amount)
        elif transaction.type in ['expenditure', 'withdraw']:
            balance.deduct_funds(transaction.amount)

        return transaction

    @api.model
    def create_enrollment_transaction(self, student_user, course):
        student_balance = self.env['owallet.balance'].search([
            ('owner_id', '=', student_user.id)
        ], limit=1)

        if not student_balance:
            raise exceptions.UserError("Student does not have a wallet balance")

        if not student_balance.has_sufficient_funds(course.cost):
            return False

        master_balance = self.env['owallet.balance'].get_master_balance()

        student_transaction = self.create({
            'balance_id': student_balance.id,
            'amount': course.cost,
            'type': 'expenditure',
            'source': 'automatic',
            'course_id': course.id,
            'description': f'Enrollment in course: {course.name}',
        })

        master_transaction = self.create({
            'balance_id': master_balance.id,
            'amount': course.cost,
            'type': 'deposit',
            'source': 'automatic',
            'course_id': course.id,
            'description': f'Payment from {student_user.name} for course: {course.name}',
        })

        return True

    @api.model
    def create_deposit_transaction(self, user, amount, description):
        if not self.env.user.has_group('owallet.group_accountant'):
            raise exceptions.AccessError("Only accountants can create deposits")

        balance = self.env['owallet.balance'].search([
            ('owner_id', '=', user.id)
        ], limit=1)

        if not balance:
            raise exceptions.UserError(f"User {user.name} does not have a wallet balance")

        return self.create({
            'balance_id': balance.id,
            'amount': amount,
            'type': 'deposit',
            'source': 'accountant',
            'description': description or f'Deposit by accountant {self.env.user.name}',
        })

    @api.model
    def create_bonus_transaction(self, teacher_user, amount, bonus_record, description):
        if not self.env.user.has_group('owallet.group_accountant'):
            raise exceptions.AccessError("Only accountants can create bonus payouts")

        teacher_balance = self.env['owallet.balance'].search([
            ('owner_id', '=', teacher_user.id)
        ], limit=1)

        if not teacher_balance:
            raise exceptions.UserError(f"Teacher {teacher_user.name} does not have a wallet balance")

        master_balance = self.env['owallet.balance'].get_master_balance()

        if not master_balance.has_sufficient_funds(amount):
            raise exceptions.UserError("Insufficient funds in master balance")

        master_transaction = self.create({
            'balance_id': master_balance.id,
            'amount': amount,
            'type': 'expenditure',
            'source': 'accountant',
            'description': f'Bonus payout to {teacher_user.name} for {bonus_record.month}/{bonus_record.year}',
            'bonus_id': bonus_record.id,
        })

        teacher_transaction = self.create({
            'balance_id': teacher_balance.id,
            'amount': amount,
            'type': 'bonus',
            'source': 'accountant',
            'description': description or f'Bonus for {bonus_record.month}/{bonus_record.year}',
            'bonus_id': bonus_record.id,
        })

        return teacher_transaction

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise exceptions.ValidationError("Transaction amount must be positive")
