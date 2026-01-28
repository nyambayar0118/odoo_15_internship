{
    'name': 'oLearn - Old',
    'category': 'Education',
    'sequence': 150,
    'summary': 'An online learning web made using Odoo framework',
    'description': """
An online learning web made using Odoo framework.
""",
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'security/security.xml',
        'security/record_rules.xml',

        'reports/teacher/report_program_info_template.xml',
        'reports/teacher/report_program_info_action.xml',

        'reports/student/report_student_performance_template.xml',
        'reports/student/report_student_performance_action.xml',

        'views/program_views.xml',
        'views/lesson_template_views.xml',
        'views/task_template_views.xml',
        'views/lesson_views.xml',
        'views/task_views.xml',

        'views/main_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}
