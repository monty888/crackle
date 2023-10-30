import logging

from aiohttp.web import Request
from monstr.event.event import Event
from server.server import ResourceAuthChecker


class MyChecker(ResourceAuthChecker):
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

    def __init__(self):

        self._auth_map = {
            f'totoro.jpg': {'ce444507e64d745999a14f7c64f253ff779acbc3cc7e1b5cb11211a76bfe4501'},
            f'monty888.jpg': {'8190f315ef037b15a487a182a12d1e7b0d171842929dfc4330107b37c10b2ed6'},
            f'scarjo.jpg': {'*'}
        }

        logging.debug(f'MyChecker::_auth_map = {self._auth_map}')

    def is_authorised(self, auth_evt: Event, request: Request) -> bool:
        ret = False

        request_url = str(request.rel_url)

        # cross origin, we'll use that - being used as auth only? e.g. nginx
        if 'X-Origin-URI' in request.headers:
            request_url = request.headers.get('X-Origin-URI')


        f_split = request_url.split('/')
        f_name = f_split[len(f_split)-1]

        print('WE SHALL CHECK ', f_name)

        # any unmapped file will be assumed unauthed
        if f_name in self._auth_map:
            ret = auth_evt.pub_key in self._auth_map[f_name] or '*' in self._auth_map[f_name]

        return ret

