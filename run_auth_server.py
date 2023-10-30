import logging
from aiohttp.web import Response, Request
from server.server import StaticServer, NIP98, ResourceAuthChecker
from example.auth_check import MyChecker
"""
    example use only as authenticator where files are being served by nginx
    see nginx_config.conf for changes to make to nginx conf file
"""

class Authenticator:

    def __init__(self, checker: ResourceAuthChecker):
        self._nip98Check = NIP98(resource_check=checker)

    def auth_route(self, request: Request):
        self._nip98Check.do_check(request)
        return Response()


def run_server(host='localhost', port=8080, is_ssl=False):
    my_server = StaticServer()
    my_auth = Authenticator(checker=MyChecker())

    # add the auth route at /auth this should match location in your nginx config
    my_server.router.add_get('/auth', my_auth.auth_route)

    my_server.start(host=host, port=8080)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    host = 'localhost'
    run_server(host=host)