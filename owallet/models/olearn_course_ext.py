from odoo import api, models


class Course(models.Model):
    _inherit = "olearn2.course"

    @api.model
    def get_current_user_balance(self):
        """Get current user's wallet balance for JS"""
        balance = self.env['owallet.balance'].sudo().search(
            [('owner_id', '=', self.env.uid)], limit=1
        )
        if balance:
            return {
                'amount': balance.amount,
                'currency_symbol': balance.currency_id.symbol,
                'currency_position': balance.currency_id.position,
            }
        return {
            'amount': 0,
            'currency_symbol': self.env.company.currency_id.symbol,
            'currency_position': self.env.company.currency_id.position,
        }
