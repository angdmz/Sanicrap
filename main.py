import aiohttp
import asyncio
from sanic import Sanic, Blueprint
from sanic.response import json
import argparse
import os

from sanic.views import HTTPMethodView

app = Sanic(name=os.getenv("APP_NAME", 'sanicrap'))
blueprint = Blueprint('projects')
ADMIN_URL = os.getenv('ADMIN_URL')
NODE_URL = os.getenv('NODE_URL')


class SimpleView(HTTPMethodView):

    def __init__(self, async_session, url):
        self.url = url
        self.session = async_session

    async def post_handler(self, request, projectid):
        async with self.session.post(self.url) as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
            return await response.json()


async def main(event_loop, session_create, host, port, debug, workers):
    async with session_create() as session:
        blueprint.add_route(SimpleView.as_view(session=session), '/<projectid:uuid>')
        app.run(host=host, port=port, debug=debug, workers=workers, loop=event_loop)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="host of the server", type=str)
    parser.add_argument("port", help="port of the server", type=int)
    parser.add_argument("--debug", help="debug enabled, overrides environment variable", action='store_true',
                        default=False)
    parser.add_argument("--workers", help="workers", type=int, default=1)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    loop.create_task(main(loop, aiohttp.ClientSession, args.host, args.port, args.debug, args.workers))
    loop.run_forever()

