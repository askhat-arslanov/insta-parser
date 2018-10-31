import aiohttp_jinja2
import aiohttp

from aiohttp import web

from utils.insta_parser.main import parse_main


class IndexView(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return


async def wshandler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                data = msg.json()
                account_name = data.get('account_name')
                await parse_main(account_name, ws)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                    ws.exception())
    return ws
