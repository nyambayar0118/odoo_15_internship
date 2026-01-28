from odoo import fields, models, api
import re


class User(models.Model):
    _name = "sisi.user"
    _description = "User Definition & Management"

    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    registry_no = fields.Char(string="Registry Number", required=True)
    email = fields.Char(string="Email Address", required=True)
    phone_no = fields.Char(string="Phone Number", required=True)
    sisi_email = fields.Char(string="SISI Email Address")
    dob = fields.Date(string="Date of Birth", required=True)
    is_active = fields.Boolean(string="Is Active", default=True)
    status = fields.Selection([("active", "Active"),
                               ("quit", "Quit"),
                               ("temporary leave", "Temporary leave"),
                               ("na", "NA"), ],
                              default="active", )

    _sql_constraints = [
        (
            "unique_registry_no",
            "unique(registry_no)",
            "The registry number must be unique.",
        ),

    ]

    @api.constrains('first_name', 'last_name')
    def _check_name(self):
        name_pattern = r'^[\u0410-\u042F\u0430-\u044F\u0401\u0451\u04E8\u04E9\u04AE\u04AF\-\' ]+$'

        for record in self:
            if not re.match(name_pattern, record.first_name.strip()):
                raise models.ValidationError(
                    'Invalid first name format!\n'
                    'First name must contain only letters, spaces, hyphens, or apostrophes.'
                )
            if not re.match(name_pattern, record.last_name.strip()):
                raise models.ValidationError(
                    'Invalid last name format!\n'
                    'Last name must contain only letters, spaces, hyphens, or apostrophes.'
                )

    @api.constrains('phone_no')
    def _check_phone(self):
        for record in self:
            if record.phone_no:
                phone_pattern = r'^[0-9]{8}$'

                if not re.match(phone_pattern, record.phone_no.strip()):
                    raise models.ValidationError(
                        'Invalid phone number format!\n'
                        'Phone number must be like: 98765432'
                    )

    @api.constrains('registry_no')
    def _check_registry_no(self):
        for record in self:
            if record.registry_no:
                registry_no_pattern = r'^[\u0410-\u042F\u0401\u04E8\u04AE]{2}[0-9]{8}$'

                if not re.match(registry_no_pattern, record.registry_no.strip()):
                    raise models.ValidationError(
                        'Invalid registration number format!\n'
                        'Registration number must be like: AA98765432'
                    )

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                if not re.match(email_pattern, record.email.strip()):
                    raise models.ValidationError(
                        'Invalid email format!\n'
                        'Email must be like: example@mail.com')

    @api.constrains('dob')
    def _check_dob(self):
        for record in self:
            if record.dob and record.dob > fields.Date.today():
                raise models.ValidationError("Date of Birth cannot be in the future.")

    @api.onchange('is_active')
    def _onchange_is_active(self):
        if self.is_active:
            self.status = 'active'
        else:
            self.status = False

    @api.onchange('status')
    def _onchange_status(self):
        if self.status != 'active':
            self.is_active = False
        else:
            self.is_active = True
