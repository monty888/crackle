import logging
from aiohttp.web import Response, Request
import ssl
from server.static_server import StaticServer, get_static_route, NIP98, ResourceAuthChecker
from monstr.event.event import Event


class MyChecker(ResourceAuthChecker):

    def is_authorised(self, auth_evt: Event, request: Request) -> bool:
        """
        basic nip98 example,
            valid nip98 evt for pk ce444507e64d745999a14f7c64f253ff779acbc3cc7e1b5cb11211a76bfe4501
                        (priv hex b71ea3ff5758a4c5ad7133765a32ed84b32b88ab55ddf86ff81c501da783e46f)
                        can see totoro.jpg
                    and
                        evt for pk 8190f315ef037b15a487a182a12d1e7b0d171842929dfc4330107b37c10b2ed6
                        (priv hex 8955c142db00c39232ff31fa77617a5eda64b461a3fc69b17fbcb952e07f79c9)
                        can see monty888.jpg

        :param auth_evt: nostr nip98 auth event
        :param request: aiohttp request obj
        :return: True/False can access resource

        in reality the check my be something like
            pks can see anything inn there own folder,
            also there might be other folders that anyone who signed valid auth can see
            (the folders might only exist as str in the request but probably make sense to actually create
            the folders in reality also)
            and mappings might come from db or nostr list events/contacts
        """

        ret = False
        if str(request.rel_url) == '/image/totoro.jpg' and \
                auth_evt.pub_key == 'ce444507e64d745999a14f7c64f253ff779acbc3cc7e1b5cb11211a76bfe4501':
            ret = True
        elif str(request.rel_url) == '/image/monty888.jpg' and \
                auth_evt.pub_key == '8190f315ef037b15a487a182a12d1e7b0d171842929dfc4330107b37c10b2ed6':
            ret = True
        elif str(request.rel_url) == '/image/scarjo.jpg':
            ret = True

        return ret


def home_route(request: Request):
    return Response(body='The home page my main dude!!!!')


def run_server(host='localhost', port=8080, is_ssl=False):

    my_nip98 = NIP98(resource_check=MyChecker())
    my_server = StaticServer()
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