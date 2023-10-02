import logging

from aiohttp.web import Response, Request
from server.static_server import StaticServer, get_static_route, NIP98


def home_route(request: Request):
    return Response(body='The home page my main dude!!!!')

def run_server():

    my_nip98 = NIP98()
    my_server = StaticServer()
    # my_server.app.middlewares.insert(0, my_nip98.middleware_check)

    image_base_dir = 'static/image/'
    html_base_dir = 'static/html/'


    my_server.router.add_get('/', home_route)
    my_server.router.add_get('/image/{tail:.*}', get_static_route(base_dir=image_base_dir,
                                                                  auth=my_nip98.do_check))
    my_server.router.add_get('/html/{tail:.*}', get_static_route(base_dir=html_base_dir))

    my_server.start()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    run_server()