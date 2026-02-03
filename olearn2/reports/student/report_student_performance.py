from odoo import models


class ReportStudentPerformance(models.AbstractModel):
    _name = 'report.olearn2.report_student_performance_template'
    _description = 'Report Student Performance'

    def _get_report_values(self, docids, data=None):
        student = self.env.user
        student_id = student.id

        # Get courses the student is enrolled in
        courses = self.env['olearn2.course'].sudo().search([
            ('student_ids', 'in', [student_id])
        ])

        course_count = len(courses)

        course_data = []

        total_lessons = 0
        total_lessons_viewed = 0
        total_tasks = 0
        total_tasks_completed = 0
        total_score = 0
        total_max_score = 0

        for course in courses:
            lessons = course.lesson_ids.filtered(lambda l: not l.hidden)
            tasks = course.task_ids.filtered(lambda t: not t.hidden)

            lesson_data = []
            for lesson in lessons:
                # Find lesson record for this student
                lesson_record = self.env['olearn2.lesson.record'].sudo().search([
                    ('lesson_id', '=', lesson.id),
                    ('student_id', '=', student_id)
                ], limit=1)

                is_viewed = lesson_record.viewed if lesson_record else False

                lesson_data.append({
                    'lesson': lesson,
                    'is_viewed': is_viewed,
                    'viewed_date': lesson_record.viewed_date if lesson_record else False,
                    'lesson_record': lesson_record
                })

                total_lessons += 1
                if is_viewed:
                    total_lessons_viewed += 1

            task_data = []
            for task in tasks:
                # Find task record for this student
                task_record = self.env['olearn2.task.record'].sudo().search([
                    ('task_id', '=', task.id),
                    ('student_id', '=', student_id)
                ], limit=1)

                score = task_record.score if task_record else 0
                max_score = task.max_score
                status = task_record.status if task_record else 'assigned'

                task_data.append({
                    'task': task,
                    'score': score,
                    'max_score': max_score,
                    'status': status,
                    'task_record': task_record
                })

                total_tasks += 1
                if status in ['completed', 'graded']:
                    total_tasks_completed += 1
                total_score += score
                total_max_score += max_score

            course_data.append({
                'course': course,
                'lesson_data': lesson_data,
                'task_data': task_data,
                'lesson_count': len(lessons),
                'task_count': len(tasks),
                'lessons_viewed': sum(1 for l in lesson_data if l['is_viewed']),
                'tasks_completed': sum(1 for t in task_data if t['status'] in ['completed', 'graded']),
                'total_score': sum(t['score'] for t in task_data),
                'total_max_score': sum(t['max_score'] for t in task_data),
            })

        overall_lesson_completion = 0
        if total_lessons > 0:
            overall_lesson_completion = (total_lessons_viewed / total_lessons) * 100

        overall_score_percentage = 0
        if total_max_score > 0:
            overall_score_percentage = (total_score / total_max_score) * 100

        return {
            'doc_ids': docids,
            'docs': courses,
            'student': student,
            'course_count': course_count,
            'course_data': course_data,
            'total_lessons': total_lessons,
            'total_lessons_viewed': total_lessons_viewed,
            'total_tasks': total_tasks,
            'total_tasks_completed': total_tasks_completed,
            'total_score': total_score,
            'total_max_score': total_max_score,
            'overall_lesson_completion': overall_lesson_completion,
            'overall_score_percentage': overall_score_percentage,
        }
