{
    'name': 'SISi',
    'category': 'Education',
    'sequence': 150,
    'summary': 'A version of SISi system made using Odoo framework',
    'description': """
This module replicates the teacher and student part of the sisi system.
""",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',

        'data/sisi.school.csv',
        'data/sisi.room.csv',
        'data/sisi.role.csv',
        'data/sisi.department.csv',
        'data/sisi.program.csv',
        'data/sisi.course.csv',

        'views/school_views.xml',
        'views/room_views.xml',
        'views/department_views.xml',
        'views/role_views.xml',
        'views/user_views.xml',
        'views/employee_views.xml',
        'views/teacher_views.xml',
        'views/student_views.xml',
        'views/program_views.xml',
        'views/course_views.xml',
        'views/course_selection_views.xml',
        'views/student_plan_item_views.xml',
        'views/grade_views.xml',
        'views/active_course_views.xml',

        'views/sisi_menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}
