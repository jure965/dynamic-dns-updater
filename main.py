import asyncio
import logging

from config import load_config, configure_logging
from api import start_webserver
from dns_updaters import init_updaters
from ip_providers import init_providers
from tasks import start_periodic_tasks

logger = logging.getLogger(__name__)


async def main():
    configure_logging()

    providers, updaters = load_config()
    init_providers(providers)
    init_updaters(updaters)

    runner = await start_webserver()
    start_periodic_tasks()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
