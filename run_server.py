from aiohttp.web import Response, Request
from server.static_server import StaticServer, get_static_route


def home_route(request: Request):
    return Response(body='The home page my main dude!!!!')

def run_server():
    my_server = StaticServer()
    base_dir = './static/images/'
    my_server.router.add_get('/', home_route)
    my_server.router.add_get('/image/{tail:.*}', get_static_route(base_dir=base_dir))

    my_server.start()

if __name__ == '__main__':
    run_server()