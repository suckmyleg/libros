# -*- coding: utf-8 -*-
{
    'name': "Libros",  
    'summary': "Gestionar libros", 
    'description': """
                    Gestor de Libros
                    ==============
                    """,  

    'application': True,
    'author': "Autor",
    'website': "website",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['base'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/libro.xml'
    ],
}
