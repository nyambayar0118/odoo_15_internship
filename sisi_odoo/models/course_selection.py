from odoo import fields, models, api


class CourseSelection(models.Model):
    _name = 'sisi.course.selection'
    _description = 'Course Selection'

    active_course_id = fields.Many2one(comodel_name='sisi.active.course')
    student_ids = fields.Many2many(comodel_name='sisi.student',
                                   domain=[])

    @api.onchange('active_course_id')
    def _get_student_ids(self):
        self.env.cr.execute("""
                            SELECT id
                            FROM sisi_student;
                            """)
        rows = self.env.cr.fetchall()
        student_ids = [r[0] for r in rows]
        student_ids = student_ids or []
        return {
            'domain': {
                'student_id': [('id', 'in', student_ids)]
            }
        }
