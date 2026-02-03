{
    'name': 'oWallet',
    'category': 'Education',
    'sequence': 150,
    'summary': 'An accounting module made using Odoo framework',
    'description': """
An accounting module for the online learning web 'oLearn' made using Odoo framework.
""",
    'depends': ['base', 'olearn2', 'web'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/wizard_deposit_guide_views.xml',
        'views/transaction_views.xml',
        'views/bonus_views.xml',
        'views/balance_views.xml',

        'views/main_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'owallet/static/src/js/course_wallet_header.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
