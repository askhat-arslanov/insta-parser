from views import IndexView, wshandler


def setup_routes(app):
    app.router.add_get('/', IndexView)
    app.router.add_get('/ws', wshandler)



