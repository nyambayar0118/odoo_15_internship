from odoo import api, fields, models, exceptions


class CreateDepositWizard(models.TransientModel):
    _name = 'owallet.create.deposit.wizard'
    _description = 'Create Deposit Wizard'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True,
        domain="[('id', '!=', 1)]",
    )

    amount = fields.Monetary(
        string='Deposit Amount',
        required=True,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    description = fields.Char(
        string='Description',
        required=True,
        default='Deposit by accountant',
    )

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise exceptions.ValidationError("Deposit amount must be positive")

    def action_create_deposit(self):
        self.ensure_one()

        if not self.env.user.has_group('owallet.group_accountant'):
            raise exceptions.AccessError("Only accountants can create deposits")

        transaction = self.env['owallet.transaction'].create_deposit_transaction(
            user=self.user_id,
            amount=self.amount,
            description=self.description
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Deposit Created',
                'message': f'Deposit of {self.amount} {self.currency_id.symbol} added to {self.user_id.name}\'s wallet',
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
