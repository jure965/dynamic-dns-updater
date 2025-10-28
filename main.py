import asyncio
import sys
from datetime import datetime, timezone, timedelta

import aiocron
import jwt
import logging

from json_log_formatter import VerboseJSONFormatter
from aiohttp import ClientSession, ServerTimeoutError

from config import load_config, config
from api import start_webserver


logger = logging.getLogger(__name__)


@aiocron.crontab("*/10 * * * * *", start=False)
async def perform_self_check():
    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=1)
    jwt_payload = {"aud": "server", "exp": expires_at}
    token = jwt.encode(jwt_payload, key=config.jwt_key)

    async with ClientSession() as session:
        try:
            async with session.post(config.self_check_url, data=token) as response:
                token = await response.text()
        except ServerTimeoutError as e:
            logger.warning(e)
            await perform_ip_update()
            return

    if response.status != 200:
        logger.warning("got non 200 status response")
        await perform_ip_update()

    try:
        jwt.decode(token, algorithms=["HS256"], key=config.jwt_key, audience="client")
    except jwt.PyJWTError as e:
        logger.warning(e)
        await perform_ip_update()

    logger.info("self check passed")


async def perform_ip_update():
    logger.info("performing ip update")

    ip_tasks = [asyncio.create_task(provider.get_ip_address()) for provider in config.providers]
    addresses = set(await asyncio.gather(*ip_tasks))

    if len(addresses) != 1:
        logger.error(f"something went wrong, got {len(addresses)} addresses: {[str(address) for address in addresses]}")

    address = addresses.pop()

    if not address:
        logger.error(f"Unable to get IP address: {address}")
        return

    logger.info(f"IP address consensus: {address}")

    dns_tasks = [asyncio.create_task(updater.set_dns_record(address)) for updater in config.updaters]
    await asyncio.gather(*dns_tasks)


def configure_logging():
    log_level = logging.getLevelName(config.log_level)
    formatter = VerboseJSONFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.root.addHandler(handler)
    logger.root.setLevel(log_level)


def start_periodic_tasks():
    perform_self_check.start()


async def main():
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
