import logging
from datetime import datetime, timezone, timedelta

import jwt
from aiohttp import web

from config import config

logger = logging.getLogger(__name__)


async def handle_ip(request):
    ip = request.headers.get("X-Forwarded-For", request.remote)
    return web.Response(text=ip)


async def handle_check(request):
    token = await request.text()

    try:
        jwt.decode(token, algorithms=["HS256"], key=config.jwt_key, audience="server")
    except jwt.PyJWTError:
        return web.Response(text="Nope", status=400)

    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=1)
    jwt_payload = {"aud": "client", "exp": expires_at}
    response_token = jwt.encode(jwt_payload, key=config.jwt_key)
    return web.Response(text=response_token, status=200)


async def start_webserver():
    app = web.Application()
    app.add_routes([
        web.get("/ip", handle_ip),
        web.post("/check", handle_check),
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, config.api_host, config.api_port)
    await site.start()
    return runner
