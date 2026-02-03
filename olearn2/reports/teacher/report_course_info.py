from odoo import models


class ReportCourseInfo(models.AbstractModel):
    _name = 'report.olearn2.report_course_info_template'
    _description = 'Report Course Info'

    def _get_report_values(self, docids, data=None):
        courses = self.env['olearn2.course'].browse(docids)

        course_data = []

        for course in courses:
            lessons = course.lesson_ids.filtered(lambda l: not l.hidden)
            tasks = course.task_ids.filtered(lambda t: not t.hidden)
            students = course.student_ids

            lesson_stats = []
            for lesson in lessons:
                # Count how many students viewed this lesson
                viewed_count = self.env['olearn2.lesson.record'].search_count([
                    ('lesson_id', '=', lesson.id),
                    ('student_id', 'in', students.ids),
                    ('viewed', '=', True)
                ])

                lesson_stats.append({
                    'lesson': lesson,
                    'viewed_count': viewed_count,
                    'total_students': len(students),
                    'view_percentage': (viewed_count / len(students) * 100) if len(students) > 0 else 0
                })

            task_stats = []
            for task in tasks:
                # Count completed tasks
                completed_count = self.env['olearn2.task.record'].search_count([
                    ('task_id', '=', task.id),
                    ('student_id', 'in', students.ids),
                    ('status', 'in', ['completed', 'graded'])
                ])

                # Calculate average score
                task_records = self.env['olearn2.task.record'].search([
                    ('task_id', '=', task.id),
                    ('student_id', 'in', students.ids),
                    ('score', '>', 0)
                ])
                avg_score = sum(t.score for t in task_records) / len(task_records) if task_records else 0

                task_stats.append({
                    'task': task,
                    'completed_count': completed_count,
                    'total_students': len(students),
                    'completion_percentage': (completed_count / len(students) * 100) if len(students) > 0 else 0,
                    'average_score': avg_score,
                    'max_score': task.max_score
                })

            student_stats = []
            for student in students:
                # Lessons viewed by this student
                lessons_viewed = self.env['olearn2.lesson.record'].search_count([
                    ('lesson_id', 'in', lessons.ids),
                    ('student_id', '=', student.id),
                    ('viewed', '=', True)
                ])

                # Tasks completed by this student
                tasks_completed = self.env['olearn2.task.record'].search_count([
                    ('task_id', 'in', tasks.ids),
                    ('student_id', '=', student.id),
                    ('status', 'in', ['completed', 'graded'])
                ])

                # Student's scores
                student_task_records = self.env['olearn2.task.record'].search([
                    ('task_id', 'in', tasks.ids),
                    ('student_id', '=', student.id)
                ])
                total_score = sum(tr.score for tr in student_task_records)
                total_max_score = sum(tr.task_id.max_score for tr in student_task_records)
                score_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0

                student_stats.append({
                    'student': student,
                    'lessons_viewed': lessons_viewed,
                    'total_lessons': len(lessons),
                    'lessons_percentage': (lessons_viewed / len(lessons) * 100) if len(lessons) > 0 else 0,
                    'tasks_completed': tasks_completed,
                    'total_tasks': len(tasks),
                    'tasks_percentage': (tasks_completed / len(tasks) * 100) if len(tasks) > 0 else 0,
                    'total_score': total_score,
                    'total_max_score': total_max_score,
                    'score_percentage': score_percentage
                })

            # Overall stats
            total_views = sum(stat['viewed_count'] for stat in lesson_stats)
            total_possible_views = len(lessons) * len(students)
            overall_view_percentage = (total_views / total_possible_views * 100) if total_possible_views > 0 else 0

            total_completions = sum(stat['completed_count'] for stat in task_stats)
            total_possible_completions = len(tasks) * len(students)
            overall_completion_percentage = (
                        total_completions / total_possible_completions * 100) if total_possible_completions > 0 else 0

            course_data.append({
                'course': course,
                'lesson_stats': lesson_stats,
                'task_stats': task_stats,
                'student_stats': student_stats,
                'overall_view_percentage': overall_view_percentage,
                'overall_completion_percentage': overall_completion_percentage
            })

        return {
            'doc_ids': docids,
            'doc_model': 'olearn2.course',
            'docs': courses,
            'course_data': course_data,
        }
