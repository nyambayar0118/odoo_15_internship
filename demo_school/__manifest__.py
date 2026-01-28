{
    'name': 'School',
    'category': 'Uncategorized',
    'sequence': 150,
    'summary': 'Keep track of teachers and students',
    'description': """
This module gives you a quick view of your contacts directory, accessible from your home page.
You can track your vendors, customers and other contacts.
""",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'wizards/teacher_wizard_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/course_views.xml',
        'views/student_course_report_views.xml',
        'report/teacher_report.xml',

        'views/school_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}
