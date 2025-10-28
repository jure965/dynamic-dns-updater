import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta

import aiocron
import jwt
import logging

from dotenv import load_dotenv
from json_log_formatter import JSONFormatter, VerboseJSONFormatter
from ruamel.yaml import YAML
from aiohttp import web, ClientSession, ServerTimeoutError

from dns_updaters import get_updater_class
from ip_providers import get_provider_class


logger = logging.getLogger(__name__)


async def handle_ip(request):
    ip = request.headers.get("X-Forwarded-For", request.remote)
    return web.Response(text=ip)


async def handle_check(request):
    token = await request.text()

    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])  # todo: secret from env var
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return web.Response(text="Nope", status=400)

    if payload.get("sub", None) != "server":
        return web.Response(text="Nope", status=400)

    response_token = jwt.encode({"sub": "client", "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, "secret")  # todo: secret from env var
    return web.Response(text=response_token, status=200)


@aiocron.crontab("*/10 * * * * *", start=False)
async def perform_self_check():
    token = jwt.encode({"sub": "server", "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=1)}, "secret")  # todo: secret from env var
    async with ClientSession() as session:
        try:
            async with session.post("http://127.0.0.1:8080/check", data=token) as response:  # todo: set url via configuration file
                token = await response.text()

            if response.status != 200:
                logger.warning("got non 200 status response")
                return

            try:
                payload = jwt.decode(token, "secret", algorithms=["HS256"])  # todo: secret from env var
            except (jwt.ExpiredSignatureError, jwt.DecodeError) as e:
                logger.warning(e)

            if payload.get("sub", None) != "client":
                logger.warning("self check failed")
                await perform_ip_update()
                return

            logger.info("self check passed")
        except ServerTimeoutError as e:
            logger.warning(e)
            logger.warning("self check failed")
            await perform_ip_update()


async def perform_ip_update():
    global updaters
    global providers

    logger.info("performing ip update")

    ip_tasks = [asyncio.create_task(provider.get_ip_address()) for provider in providers]
    addresses = set(await asyncio.gather(*ip_tasks))

    if len(addresses) != 1:
        logger.error(f"something went wrong, got {len(addresses)} addresses: {[str(address) for address in addresses]}")

    address = addresses.pop()

    if not address:
        logger.error(f"Unable to get IP address: {address}")
        return

    logger.info(f"IP address consensus: {address}")

    dns_tasks = [asyncio.create_task(updater.set_dns_record(address)) for updater in updaters]
    await asyncio.gather(*dns_tasks)


def load_config():
    yaml = YAML(typ="safe")

    with open("config.yaml", "r") as config_file:
        config = yaml.load(config_file)

    global providers
    providers = []
    for provider in config["providers"]:
        provider_class = get_provider_class(provider["type"])
        provider_params = provider.get("params", None)

        if provider_params:
            providers.append(provider_class(**provider_params))
        else:
            providers.append(provider_class())

    global updaters
    updaters = []
    for updater in config["updaters"]:
        updater_class = get_updater_class(updater["type"])
        updater_params = updater.get("params", None)
        updaters.append(updater_class(**updater_params))


providers = []
updaters = []


def configure_logging():
    log_level = logging.getLevelName(os.environ.get("LOG_LEVEL", "WARNING"))
    formatter = VerboseJSONFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.root.addHandler(handler)
    logger.root.setLevel(log_level)


async def start_webserver():
    app = web.Application()
    app.add_routes([
        web.get("/ip", handle_ip),
        web.post("/check", handle_check),
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    return runner


def start_periodic_tasks():
    perform_self_check.start()


async def main():
    load_dotenv()
    load_config()
    configure_logging()

    runner = await start_webserver()
    start_periodic_tasks()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
