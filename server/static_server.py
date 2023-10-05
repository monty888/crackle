from abc import abstractmethod
import logging
import os.path
import base64
import json
from datetime import datetime

import aiohttp
from aiohttp import web
from aiohttp.web import Request, FileResponse, Response, UrlDispatcher, \
    HTTPNotFound, HTTPFound, HTTPException, HTTPUnauthorized
from monstr.event.event import Event
from monstr.util import util_funcs

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


class ResourceAuthChecker:

    @abstractmethod
    def is_authorised(self, auth_evt: Event, request: Request) -> bool:
        pass


class NIP98:

    def __init__(self,
                 time_window: int =60,
                 resource_check: ResourceAuthChecker = None):

        self._time_window = time_window

        # to check futher if resource/url can be accessed,
        # not called until we already passed basic NIP98 checks
        self._resource_check = resource_check

    def do_check(self, request):
        logging.debug(f'NIP98:do_check: {request.url}')

        auth_head = request.headers.get('Auth')
        is_auth = False
        try:
            if auth_head:
                auth_str = base64.b64decode(auth_head).decode()
                auth_evt = Event.from_JSON(json.loads(auth_str))
                if auth_evt.is_valid():
                    # at this point we have a valid event in the http auth header
                    # now we'll check that its valid by NIP98 criteria
                    # that is
                    #   correct kind +
                    #       in a reasonable time window to the server +
                    #       u tag url matches request url


                    # create min and max accept ticks, time window is split 80% to before
                    # our clock
                    now = util_funcs.date_as_ticks(datetime.now())
                    min_accept = now - int(self._time_window*.8)
                    max_accept = min_accept + self._time_window

                    if auth_evt.kind == 27235 and \
                            min_accept <= auth_evt.created_at_ticks <= max_accept and \
                            auth_evt.tags.get_tag_value_pos('u', default='') == str(request.url):

                        if self._resource_check is None or \
                                self._resource_check.is_authorised(auth_evt=auth_evt,
                                                                   request=request):
                            is_auth = True

        except Exception as e:
            print(e)

        if not is_auth:
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
