from aiohttp import web
from aiohttp.web import Request, FileResponse


async def test_home(request: Request):
    return web.Response(text='mother fucker')


async def test_file(request: Request):
    base_dir = './static/images/'
    file_name = request.url.name

    print(request.headers.items())

    print('auth', request.headers.get('Auth'))

    return FileResponse(f'{base_dir}{file_name}')


class StaticServer:

    def __init__(self):
        self._app = web.Application()
        self._app.router.add_get('/', test_home)
        self._app.router.add_get('/image/{tail:.*}', test_file)

    def start(self):
        web.run_app(self._app)


