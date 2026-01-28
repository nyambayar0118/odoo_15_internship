# -*- coding: utf-8 -*-
from odoo import models, fields, tools


class StudentCourseReport(models.Model):
    _name = 'demo_school.student_course_report'
    _description = 'Student - Course Report'
    _auto = False
    _rec_name = 'student_name'
    _order = 'student_name'

    # fields must match columns of the SQL view
    student_id = fields.Many2one('demo_school.student', readonly=True)
    student_name = fields.Char(readonly=True)
    course_id = fields.Many2one('demo_school.course', readonly=True)
    course_name = fields.Char(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    s.id AS id,
                    s.id AS student_id,
                    s.name AS student_name,
                    s.course_id AS course_id,
                    c.name AS course_name
                FROM demo_school_student s
                LEFT JOIN demo_school_course c
                    ON c.id = s.course_id
            )
        """)

    def action_report(self):
        for i in range(20):
            print("Generating PDF report...")
        return self.env.ref('demo_school.action_report_pdf_ticket').report_action(self)
