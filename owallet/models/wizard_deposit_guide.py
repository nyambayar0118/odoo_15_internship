from odoo import models, fields, api


class DepositWizardGuide(models.TransientModel):
    _name = 'owallet.deposit.wizard.guide'
    _description = 'Данс цэнэглэх заавар'

    guide = fields.Text(
        string='Guide',
        default=lambda self: self._default_guide(),
        readonly=True
    )

    user_balance = fields.Monetary(
        string='Current Balance',
        default=lambda self: self._default_user_balance(),
        currency_field='currency_id',
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self._default_currency_id(),
        readonly=True
    )

    def _default_guide(self):
        return """Та системийн дансандаа мөнгө байршуулхын тулд дараах зааврыг дагана уу:

1. Байгууллагын данс руу шилжүүлэг хийх:
   Банк: Худалдаа Хөгжлийн Банк
   Дансны дугаар: MN600004000437013755
   Данс эзэмшигчийн нэр: Нямбаяр Очир

2. Гүйлгээний утга дээр та өөрийн нэвтрэх нэрийг бичнэ.

3. Гүйлгээ хийгдсэнээс 24 цагийн дотор систем дээрх таны дансны үлдэгдэл шинэчлэгдэх болно.

Асуудал гарвал дараах хаягаар хандана уу: nyambayar2014@gmail.com"""

    def _default_user_balance(self):
        balance = self.env.user.balance_id
        return balance.amount if balance else 0.0

    def _default_currency_id(self):
        balance = self.env.user.balance_id
        return balance.currency_id.id if balance else self.env.company.currency_id.id
