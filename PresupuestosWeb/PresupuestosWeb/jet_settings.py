JET_DEFAULT_THEME = 'green'
JET_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'
JET_APP_INDEX_DASHBOARD = 'dashboard.CustomAppIndexDashboard'
JET_SIDE_MENU_COMPACT = False
JET_SIDE_MENU_ITEMS = [
    {'label':'Pedidos','items':[
            {'name':'app.notapedido'},
            {'name':'app.notaremision'},
            {'name':'app.recepcion'},
        ]
    },
    {'label':'Compras','items':[
            {'name':'app.solicitudpresupuesto'},
            {'name':'app.ordencompra'},
            {'name':'app.facturacompra'},
            {'name':'app.proveedor'},
        ]
    },
    {'label':'Articulos','items':[
            {'name':'app.articulo'},
            {'name':'app.categoriaarticulo'},
            {'name':'app.tipoarticulo'},
            {'name':'app.unidadmedida'},
        ]
    },
    {'label':'Datos Maestros','items':[
            {'name':'app.sucursal'},
            {'name':'app.departamento'},
            {'name':'app.departamentosucursal'},
            {'name':'app.moneda'},
            {'name':'app.plazopago'},
        ]
    },
    {'app_label':'auth','items':[
            {'name':'group'},
            {'name':'user'},
        ]
    },
]

