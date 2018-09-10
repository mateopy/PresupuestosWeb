
JET_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
JET_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'
JET_SIDE_MENU_COMPACT = False
JET_SIDE_MENU_ITEMS = [
    {'label':'Operaciones','items':[
            {'name':'app.notapedido'},
            {'name':'app.notaremision'},
            {'name':'app.recepcion'},
        ]
    },
    {'label':'Articulos','items':[
            {'name':'app.articulo'},
            {'name':'app.categoriaarticulo'},
            {'name':'app.tipoarticulo'},
            {'name':'app.unidadmedida'},
        ]
    },
    {'label':'Datos Generales','items':[
            {'name':'app.sucursal'},
            {'name':'app.departamento'},
            {'name':'app.departamentosucursal'},
        ]
    },
    {'app_label':'auth','items':[
            {'name':'group'},
            {'name':'user'},
        ]
    },
]

