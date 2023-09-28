from server.static_server import StaticServer


def run_server():
    my_server = StaticServer()
    my_server.start()

if __name__ == '__main__':
    run_server()