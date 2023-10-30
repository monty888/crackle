import logging
from aiohttp.web import Response, Request
import ssl
from server.server import StaticServer, get_static_route, NIP98, ResourceAuthChecker
from example.auth_check import MyChecker


def home_route(request: Request):
    return Response(body='The home page my main dude!!!!')


def run_server(host='localhost', port=8080, is_ssl=False):

    my_server = StaticServer()
    my_nip98 = NIP98(resource_check=MyChecker())
    # my_server.app.middlewares.insert(0, my_nip98.middleware_check)

    image_base_dir = 'static/image/'
    html_base_dir = 'static/html/'
    script_base_dir = 'static/script/'

    my_server.router.add_get('/', home_route)
    my_server.router.add_get('/image/{tail:.*}', get_static_route(base_dir=image_base_dir,
                                                                  auth=my_nip98.do_check))
    my_server.router.add_get('/html/{tail:.*}', get_static_route(base_dir=html_base_dir))
    my_server.router.add_get('/script/{tail:.*}', get_static_route(base_dir=script_base_dir))

    ssl_context = None
    if is_ssl:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('/home/monty/.nostrpy/my_cert.pem', '/home/monty/.nostrpy/my_privatekey.pem')

    my_server.start(host=host, port=8080, ssl_context=ssl_context)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    host = 'localhost'
    is_ssl = False

    run_server(host=host, is_ssl=is_ssl)