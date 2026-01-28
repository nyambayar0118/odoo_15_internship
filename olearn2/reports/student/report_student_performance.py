from odoo import models


class ReportProgram(models.AbstractModel):
    _name = 'report.olearn.report_student_performance_template'
    _description = 'Report Student Performance'

    def _get_report_values(self, docids, data=None):
        student = self.env.user
        student_id = student.id

        programs = self.env['olearn.program'].search([
            ('student_ids', 'in', [student_id])
        ])

        program_count = len(programs)

        program_data = []

        total_lessons = 0
        total_lessons_viewed = 0
        total_tasks = 0
        total_tasks_completed = 0
        total_score = 0
        total_max_score = 0

        for program in programs:
            lesson_templates = program.lesson_template_ids
            task_templates = program.task_template_ids

            lesson_data = []
            for lesson_template in lesson_templates:
                lesson = self.env['olearn.lesson'].search([
                    ('lesson_template_id', '=', lesson_template.id),
                    ('student_id', '=', student_id)
                ], limit=1)

                is_viewed = lesson.is_viewed if lesson else False

                lesson_data.append({
                    'template': lesson_template,
                    'is_viewed': is_viewed,
                    'lesson_instance': lesson
                })

                total_lessons += 1
                if is_viewed:
                    total_lessons_viewed += 1

            task_data = []
            for task_template in task_templates:
                task = self.env['olearn.task'].search([
                    ('task_template_id', '=', task_template.id),
                    ('student_id', '=', student_id)
                ], limit=1)

                score = task.score if task else 0
                max_score = task_template.max_score
                status = task.status if task else 'not_started'

                task_data.append({
                    'template': task_template,
                    'score': score,
                    'max_score': max_score,
                    'status': status,
                    'task_instance': task
                })

                total_tasks += 1
                if status in ['completed', 'graded']:
                    total_tasks_completed += 1
                total_score += score
                total_max_score += max_score

            program_completion = 0
            if total_lessons > 0:
                program_completion = (total_lessons_viewed / total_lessons) * 100

            program_score_percentage = 0
            if total_max_score > 0:
                program_score_percentage = (total_score / total_max_score) * 100

            program_data.append({
                'program': program,
                'lesson_data': lesson_data,
                'task_data': task_data,
                'lesson_count': len(lesson_templates),
                'task_count': len(task_templates),
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
            'docs': programs,
            'student': student,
            'program_count': program_count,
            'program_data': program_data,
            'total_lessons': total_lessons,
            'total_lessons_viewed': total_lessons_viewed,
            'total_tasks': total_tasks,
            'total_tasks_completed': total_tasks_completed,
            'total_score': total_score,
            'total_max_score': total_max_score,
            'overall_lesson_completion': overall_lesson_completion,
            'overall_score_percentage': overall_score_percentage,
        }
