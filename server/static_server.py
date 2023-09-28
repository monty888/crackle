import logging
from aiohttp import web
from aiohttp.web import Request, FileResponse, Response, UrlDispatcher

class AuthenticationFailedException(Exception):
    pass


def get_dir_list_route():
    return Response(body='TODO')


def get_static_route(base_dir: str = '.',
                     auth: callable = None,
                     extensions: str = None,
                     error_map: dict = None
                     ):

    if error_map is None:
        error_map = {}

    def do_error(err: Exception):
        print(type(err))
        return Response(status=401,
                        body=str(err),
                        reason='some reason')

    async def static_route(request: Request):
        file_name = request.url.name

        try:
            if auth:
                success, err = auth(request.headers.get('Auth'))

                if err is not None:
                    raise AuthenticationFailedException('some err')
            else:
                logging.debug(f'static_route:: no auth required {request.url}')

            print(request.headers.items())

            print('auth', request.headers.get('Auth'))

            return FileResponse(f'{base_dir}{file_name}')

        except AuthenticationFailedException as ae:
            return do_error(ae)
        except Exception as e:
            print('exception!!!!!')
            return do_error(e)

    return static_route


class StaticServer:

    def __init__(self):
        self._app = web.Application()
        self._app.ha

    def start(self):
        web.run_app(self._app)

    @property
    def app(self) -> web.Application:
        return self._app

    @property
    def router(self) -> UrlDispatcher:
        return self._app.router
