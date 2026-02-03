{
    'name': 'oLearn - New',
    'category': 'Education',
    'sequence': 150,
    'summary': 'An online learning web made using Odoo framework',
    'description': """
An online learning web made using Odoo framework.
""",
    'depends': ['base', 'website'],
    'data': [
        'views/main_page.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

        'security/security.xml',
        'security/record_rules.xml',

        'reports/student/report_student_performance_action.xml',
        'reports/student/report_student_performance_template.xml',
        'reports/teacher/report_course_info_action.xml',
        'reports/teacher/report_course_info_template.xml',

        'views/course_views.xml',
        'views/lesson_views.xml',
        'views/task_views.xml',
        'views/lesson_record_views.xml',
        'views/task_record_views.xml',

        'views/main_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}
