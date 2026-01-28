from odoo import fields, models


class Course(models.Model):
    _name = "sisi.course"
    _description = "Course Definition & Management"

    index = fields.Char(string="Course Index", required=True)
    name = fields.Char(string="Course Name", required=True)
    credit_amount = fields.Integer(string="Course Credit Amount", required=True)
    description = fields.Text(string="Course Description")
    created_year = fields.Integer(string="Created Year", required=True)
    type = fields.Selection([("general basic", "General Basic"), ("professional basic", "Professional Basic"),
                             ("professional", "Professional"), ("other", "Other"), ],
                            required=True, default="general basic")
    form = fields.Selection([
        ('lecture only', 'Lecture Only'),
        ('lecture and seminar', 'Lecture and Seminar'),
        ('lecture and laboratory', 'Lecture and Laboratory'),
        ('seminar only', 'Seminar Only'),
        ('internship', 'Internship'),
        ('diploma work', 'Diploma Work'), ],
        required=True)

    lecture_session = fields.Integer(string="Lecture Session", required=True, default=1)
    lecture_count = fields.Integer(string="Lecture Count", default=16)

    lecture_duration = fields.Selection([
        ('0', 'No Lecture'),
        ('90', '90 minutes'),
        ('135', '135 minutes'),
        ('180', '180 minutes'),
    ],
        default="90",
        string="Lecture Duration",
    )

    def name_get(self):
        result = []
        for course in self:
            display_name = f"{course.index} {course.name}"
            result.append((course.id, display_name))
        return result
