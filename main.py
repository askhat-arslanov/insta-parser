import asyncio
import os

import aiohttp_jinja2
import jinja2
from aiohttp import web

from routes import setup_routes

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)

app = web.Application()
aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader('templates/'))
setup_routes(app)
app.router.add_static('/static', 'static', name='static')
app.router.add_static('/archives', 'archives', name='archives')

if __name__ == '__main__':
    web.run_app(app, port=os.environ.get('PORT', '5000'))
