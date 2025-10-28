import logging
import aiocron
import jwt

from aiohttp import ClientSession, ServerTimeoutError
from datetime import datetime, timezone, timedelta
from config import config
from dns_updaters import perform_ip_update

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

    logger.debug("self check passed")


def start_periodic_tasks():
    perform_self_check.start()
