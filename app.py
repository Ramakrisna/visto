from tornado.options import define, options
from views import URLParserHandler
from models import DB
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient

define("port", default=8888, help="run on the given port", type=int)


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(
        handlers=[
            ("/parse_url", URLParserHandler),
            # ("/add_user", ExtractElement)
        ],
        db=DB)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    print(f'Listening on http://localhost:{options.port}')
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()

