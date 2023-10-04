import logging
import os.path
from aiohttp import web
from aiohttp.web import Request, FileResponse, Response, UrlDispatcher, \
    HTTPNotFound, HTTPFound, HTTPException, HTTPUnauthorized


class ServerErrors:
    @web.middleware
    async def errors_middleware(self, request, handler):
        """
        doesn't do much at the moment except catch any non HTTPExceptions and return them
        NOTE stream exceptions can't be caught this way and I'm not sure how you're ment to get them...
        could be used to modify what happens on errs

        :param request:
        :param handler:
        :return:
        """
        try:
            response = await handler(request)

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e

            return Response(status=500,
                            body=str(f'our own bad exception: {e}'),
                            reason='wtf')

        return response


class NIP98:

    def do_check(self, request):
        print(f'check auth....{request.rel_url}')
        auth_head = request.headers.get('Auth')

        print('auth', auth_head)

        if auth_head is None or auth_head != 'ce444507e64d745999a14f7c64f253ff779acbc3cc7e1b5cb11211a76bfe4501':



            raise HTTPUnauthorized()

    @web.middleware
    async def middleware_check(self, request, handler):
        self.do_check(request)
        return await handler(request)


def get_static_route(base_dir: str = '.',
                     auth: callable = None,
                     extensions: str = None
                     ):

    async def static_route(request: Request):
        print('WTF!!!!')
        file_name = request.url.name

        if auth:
            auth(request)
        else:
            logging.debug(f'static_route:: no auth required {request.url}')

        full_name = f'{base_dir}{file_name}'
        logging.debug(f'static_route:: dir -  {base_dir} file - {full_name}')
        # FIXME: couldn't work out how to catch the err from FileResponse
        #  so for now do ourself and raise, maybe this is best we can do?
        if not os.path.isfile(full_name):
            raise HTTPNotFound(text=f'file not found {full_name}')

        return FileResponse(full_name)

    return static_route


class StaticServer:

    def __init__(self):

        my_errors = ServerErrors()
        self._app = web.Application(middlewares=[my_errors.errors_middleware])

    def start(self, **kargs):
        web.run_app(self._app, **kargs)

    @property
    def app(self) -> web.Application:
        return self._app

    @property
    def router(self) -> UrlDispatcher:
        return self._app.router
