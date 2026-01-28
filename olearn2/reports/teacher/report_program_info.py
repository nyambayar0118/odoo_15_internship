from odoo import models


class ReportProgramInfo(models.AbstractModel):
    _name = 'report.olearn.report_program_info_template'
    _description = 'Report Program Info'

    def _get_report_values(self, docids, data=None):
        programs = self.env['olearn.program'].browse(docids)

        program_data = []

        for program in programs:
            lesson_templates = program.lesson_template_ids
            task_templates = program.task_template_ids

            lesson_stats = []
            for lesson_template in lesson_templates:
                viewed_count = len([
                    lesson for lesson in lesson_template.lesson_ids
                    if lesson.is_viewed and lesson.student_id in program.student_ids
                ])

                lesson_stats.append({
                    'template': lesson_template,
                    'viewed_count': viewed_count,
                    'total_students': len(program.student_ids),
                    'view_percentage': (viewed_count / len(program.student_ids) * 100) if len(
                        program.student_ids) > 0 else 0
                })

            task_stats = []
            for task_template in task_templates:
                completed_count = len([
                    task for task in task_template.task_ids
                    if task.status in ['completed', 'graded'] and task.student_id in program.student_ids
                ])

                tasks = [
                    task for task in task_template.task_ids
                    if task.student_id in program.student_ids and task.score > 0
                ]
                avg_score = sum(t.score for t in tasks) / len(tasks) if tasks else 0

                task_stats.append({
                    'template': task_template,
                    'completed_count': completed_count,
                    'total_students': len(program.student_ids),
                    'completion_percentage': (completed_count / len(program.student_ids) * 100) if len(
                        program.student_ids) > 0 else 0,
                    'average_score': avg_score,
                    'max_score': task_template.max_score
                })

            student_stats = []
            for student in program.student_ids:
                lessons_viewed = len([
                    lesson for lesson in self.env['olearn.lesson'].search([
                        ('lesson_template_id', 'in', lesson_templates.ids),
                        ('student_id', '=', student.id),
                        ('is_viewed', '=', True)
                    ])
                ])

                tasks_completed = len([
                    task for task in self.env['olearn.task'].search([
                        ('task_template_id', 'in', task_templates.ids),
                        ('student_id', '=', student.id),
                        ('status', 'in', ['completed', 'graded'])
                    ])
                ])

                student_tasks = self.env['olearn.task'].search([
                    ('task_template_id', 'in', task_templates.ids),
                    ('student_id', '=', student.id)
                ])
                total_score = sum(task.score for task in student_tasks)
                total_max_score = sum(task.task_template_id.max_score for task in student_tasks)
                score_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0

                student_stats.append({
                    'student': student,
                    'lessons_viewed': lessons_viewed,
                    'total_lessons': len(lesson_templates),
                    'lessons_percentage': (lessons_viewed / len(lesson_templates) * 100) if len(
                        lesson_templates) > 0 else 0,
                    'tasks_completed': tasks_completed,
                    'total_tasks': len(task_templates),
                    'tasks_percentage': (tasks_completed / len(task_templates) * 100) if len(task_templates) > 0 else 0,
                    'total_score': total_score,
                    'total_max_score': total_max_score,
                    'score_percentage': score_percentage
                })

            total_views = sum(stat['viewed_count'] for stat in lesson_stats)
            total_possible_views = len(lesson_templates) * len(program.student_ids)
            overall_view_percentage = (total_views / total_possible_views * 100) if total_possible_views > 0 else 0

            total_completions = sum(stat['completed_count'] for stat in task_stats)
            total_possible_completions = len(task_templates) * len(program.student_ids)
            overall_completion_percentage = (
                    total_completions / total_possible_completions * 100) if total_possible_completions > 0 else 0

            program_data.append({
                'program': program,
                'lesson_stats': lesson_stats,
                'task_stats': task_stats,
                'student_stats': student_stats,
                'overall_view_percentage': overall_view_percentage,
                'overall_completion_percentage': overall_completion_percentage
            })

        return {
            'doc_ids': docids,
            'doc_model': 'olearn.program',
            'docs': programs,
            'program_data': program_data,
        }
