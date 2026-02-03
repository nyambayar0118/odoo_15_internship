from odoo import api, fields, models, exceptions


class Users(models.Model):
    _inherit = "res.users"

    balance_id = fields.Many2one(
        'owallet.balance',
        string='Wallet Balance',
        readonly=True
    )

    @api.model
    def create(self, vals):
        user = super().create(vals)

        # Create balance for new user
        balance = self.env["owallet.balance"].sudo().create({
            "owner_id": user.id,
            "amount": 0.0
        })

        user.balance_id = balance.id

        return user


class Balance(models.Model):
    _name = "owallet.balance"
    _description = "Owallet Balance"
    _rec_name = "owner_id"

    owner_id = fields.Many2one(
        comodel_name="res.users",
        string="Wallet Owner",
        required=True,
        ondelete="cascade",
        index=True,
    )

    amount = fields.Monetary(
        string="Balance Amount",
        default=0.0,
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    transaction_ids = fields.One2many(
        'owallet.transaction',
        'balance_id',
        string='Transactions'
    )

    is_master = fields.Boolean(
        string="Master Balance",
        default=False,
        help="Master balance holds all system funds"
    )

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise exceptions.ValidationError("Wallet amount can't be negative.")

    _sql_constraints = [
        ('unique_user_balance',
         'UNIQUE(owner_id)',
         'A user can only have one balance')
    ]

    def has_sufficient_funds(self, amount):
        """Check if balance has sufficient funds"""
        self.ensure_one()
        return self.amount >= amount

    def add_funds(self, amount):
        """Add funds to balance"""
        self.ensure_one()
        if amount <= 0:
            raise exceptions.ValidationError("Amount must be positive")
        self.write({'amount': self.amount + amount})

    def deduct_funds(self, amount):
        """Deduct funds from balance"""
        self.ensure_one()
        if amount <= 0:
            raise exceptions.ValidationError("Amount must be positive")
        if not self.has_sufficient_funds(amount):
            raise exceptions.ValidationError("Insufficient funds")
        self.write({'amount': self.amount - amount})

    @api.model
    def get_master_balance(self):
        """Get or create master balance for admin"""
        admin_user = self.env.ref('base.user_admin')
        master_balance = self.search([('owner_id', '=', admin_user.id)], limit=1)

        if not master_balance:
            master_balance = self.sudo().create({
                'owner_id': admin_user.id,
                'amount': 0.0,
                'is_master': True
            })

        return master_balance

    @api.model
    def action_open_my_wallet(self):
        """Open the current user's wallet balance"""
        # Find or create the user's balance
        balance = self.sudo().search([('owner_id', '=', self.env.user.id)], limit=1)

        if not balance:
            # If balance doesn't exist, create it
            balance = self.sudo().create({'owner_id': self.env.user.id})

        return {
            'name': 'My Balance',
            'type': 'ir.actions.act_window',
            'res_model': 'owallet.balance',
            'view_mode': 'form',
            'res_id': balance.id,
            'view_id': self.env.ref('owallet.view_my_wallet_form').id,
            'target': 'current',
            'context': {'create': False, 'delete': False, 'edit': False},
        }

    @api.model
    def action_open_master_balance(self):
        """Open the master balance"""
        master_balance = self.get_master_balance()

        return {
            'name': 'Master Balance',
            'type': 'ir.actions.act_window',
            'res_model': 'owallet.balance',
            'view_mode': 'form',
            'res_id': master_balance.id,
            'view_id': self.env.ref('owallet.view_owallet_balance_form').id,
            'target': 'current',
            'context': {'create': False, 'delete': False},
        }
