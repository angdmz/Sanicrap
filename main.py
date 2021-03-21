from http.client import TOO_MANY_REQUESTS, FORBIDDEN

import aiohttp
from sanic import Sanic, Blueprint
from sanic.response import json, empty
import argparse
import os
import requests

from sanic.views import HTTPMethodView

ADMIN_URL = os.getenv('ADMIN_URL')
NODE_URL = os.getenv('NODE_URL')


class Project:

    def __init__(self, name, max_requests_per_month, max_requests_per_second):
        self.max_requests_per_second = max_requests_per_second
        self.max_requests_per_month = max_requests_per_month
        self.name = name

    @staticmethod
    def from_response(status_code, response):
        if status_code == 200:
            decoded = response
            return Project(decoded['name'], decoded['max_requests_per_second'], decoded['max_requests_per_month'])

    def format(self, formatter):
        return formatter.map({'name': self.name,
                              'max_requests_per_month': self.max_requests_per_month,
                              'max_requests_per_second': self.max_requests_per_second})


class ProjectRegisterSystem:

    def __init__(self, session, admin_url, cache):
        self.admin_url = admin_url
        self.session = session
        self.cache = cache

    async def is_project(self, project_id):
        if self.cache.in_cache(project_id):
            return True

        async with self.session.get(self.admin_url) as admin_response:
            res = await admin_response.json()
            project = Project.from_response(admin_response.status_code, res)
            self.cache.register(project)


class SimpleView(HTTPMethodView):

    def __init__(self, admin_url, node_url, hit_register, cache):
        self.cache = cache
        self.hit_register = hit_register
        self.node_url = node_url
        self.admin_url = admin_url

    async def post(self, request, project_id):

        async with request.app.session.get(f"{self.admin_url}/api/v1/projects/{project_id}") as admin_response:
            res = await admin_response.json()
            if admin_response.status == 200:
                self.cache.add(project_id)
                self.hit_register.setdefault(project_id, 0)
                if res['max_requests_per_month'] > self.hit_register[project_id]:
                    self.hit_register[project_id] += 1
                    async with request.app.session.post(self.node_url, json=request.json) as response:
                        returnable = await response.json()
                        return json(returnable)
                else:
                    return empty(status=TOO_MANY_REQUESTS)
            else:
                return empty(status=FORBIDDEN)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="host of the server", type=str)
    parser.add_argument("port", help="port of the server", type=int)
    parser.add_argument("--debug", help="debug enabled, overrides environment variable", action='store_true',
                        default=False)
    parser.add_argument("--workers", help="server workers", type=int, default=1)
    args = parser.parse_args()

    app = Sanic(name=os.getenv("APP_NAME", 'sanicrap'))
    blueprint = Blueprint('projects')


    @app.listener('before_server_start')
    async def create_session(sanicapp, loop):
        session = aiohttp.ClientSession(loop=loop)
        sanicapp.session = session

    view = SimpleView.as_view(node_url=NODE_URL, admin_url=ADMIN_URL, hit_register=dict(), cache=set())

    blueprint.add_route(view, '/<project_id:uuid>')
    app.blueprint(blueprint)

    app.run(host=args.host, port=args.port, debug=args.debug, workers=args.workers)




