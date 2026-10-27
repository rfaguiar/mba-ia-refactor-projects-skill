from views import pedido_views, produto_views, sistema_views, usuario_views


def register_routes(app):
    for modulo in (produto_views, usuario_views, pedido_views, sistema_views):
        app.register_blueprint(modulo.bp)
