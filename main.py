from sanic import Sanic
from sanic.response import json
import argparse

app = Sanic()

@app.route('/v1/ok', methods=['GET'])
async def post_handler(request):
    return json({"response":"hey all good"})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="host of the server", type=str)
    parser.add_argument("port", help="port of the server", type=int)
    parser.add_argument("--debug", help="debug enabled, overrides environment variable", action='store_true', default=False)
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
