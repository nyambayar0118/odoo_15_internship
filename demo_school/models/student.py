# -*- coding: utf-8 -*-
from odoo import api, fields, models
import re
from PIL import Image
import base64
import io


class Student(models.Model):
    _name = 'demo_school.student'
    _description = 'Student info'

    name = fields.Char(string='Name', required=True, tracking=True)
    registration = fields.Char(string='Registration Number', required=True, tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender'
    )
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    date_of_birth = fields.Date(string='Date of Birth')

    # Many 2 one to course
    course_id = fields.Many2one(
        'demo_school.course',
        string='Course',
        ondelete='set null',
        help='Select the course for this student'
    )

    # Many 2 one to teacher
    teacher_id = fields.Many2one(
        'demo_school.teacher',
        string='Teacher',
        ondelete='set null',
        help='Select the teacher for this student'
    )

    image = fields.Image(string='Student Image', help='Put Image here')

    def _crop_image_to_square(self, image_base64):
        if not image_base64:
            return image_base64

        try:
            # Decode the base64 image
            img_data = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(img_data))

            width, height = img.size

            # Calculate square crop area (center crop)
            min_side = min(width, height)
            left = (width - min_side) // 2
            top = (height - min_side) // 2
            right = left + min_side
            bottom = top + min_side

            img_cropped = img.crop((left, top, right, bottom))

            # Resize to desired output (optional)
            img_cropped = img_cropped.resize((256, 256))

            # Convert back to base64
            buffer = io.BytesIO()
            img_cropped.save(buffer, format=img.format or 'PNG')
            return base64.b64encode(buffer.getvalue())

        except Exception:
            return image_base64

    # -------------------------------
    # Override CREATE
    # -------------------------------

    @api.model
    def create(self, vals):
        if vals.get("image"):
            vals["image"] = self._crop_image_to_square(vals["image"])
        return super().create(vals)

    # -------------------------------
    # Override WRITE
    # -------------------------------
    def write(self, vals):
        if vals.get("image"):
            vals["image"] = self._crop_image_to_square(vals["image"])
        return super().write(vals)

    is_adult = fields.Boolean(string='Is Adult', compute='_compute_is_adult', store=True)
    active = fields.Boolean(default=True)

    @api.constrains('date_of_birth')
    def _check_dob(self):
        for record in self:
            if record.date_of_birth and record.date_of_birth > fields.Date.today():
                raise models.ValidationError("Date of Birth cannot be in the future.")

    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age < 6:
                raise models.ValidationError("The student must be older than 5.")

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

                if not re.match(email_pattern, record.email.strip()):
                    raise models.ValidationError(
                        'Invalid email format!\n'
                        'Email must be like: example@domain.com'
                    )

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone:
                phone_pattern = r'^[0-9]{8}$'

                if not re.match(phone_pattern, record.phone.strip()):
                    raise models.ValidationError(
                        'Invalid phone number format!\n'
                        'Phone number must be like: 98765432'
                    )

    @api.constrains('registration')
    def _check_registration(self):
        for record in self:
            if record.registration:
                registration_pattern = r'^[A-Z]{2,4}[0-9]{8}$'

                if not re.match(registration_pattern, record.registration.strip()):
                    raise models.ValidationError(
                        'Invalid registration number format!\n'
                        'Registration number must be like: UP98765432'
                    )

    @api.depends('age')
    def _compute_is_adult(self):
        for record in self:
            record.is_adult = record.age >= 18 if record.age else False

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                age = today.year - record.date_of_birth.year - (
                        (today.month, today.day) < (record.date_of_birth.month, record.date_of_birth.day)
                )
                record.age = age
            else:
                record.age = 0

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            return {'domain': {
                'teacher_id': [('id', 'in', self.course_id.teacher_ids.ids)]
            }}
        else:
            return {'domain': {'teacher_id': []}}
