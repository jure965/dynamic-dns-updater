import asyncio

import aiocron
from dotenv import load_dotenv
from ruamel.yaml import YAML
from aiohttp import web, ClientSession

from dns_updaters import get_updater_class
from ip_providers import get_provider_class


async def handle(request):
    ip = request.headers.get("X-Forwarded-For", request.remote)
    return web.Response(text=ip)


@aiocron.crontab("* * * * *", start=False)
async def perform_self_check():
    async with ClientSession() as session:
        async with session.get("http://127.0.0.1:8080/ip") as response:  # todo: set url via configuration file
            print(await response.text())


async def perform_check(providers, updaters):
    ip_tasks = [asyncio.create_task(provider.get_ip_address()) for provider in providers]
    addresses = set(await asyncio.gather(*ip_tasks))

    if len(addresses) != 1:
        print(f"something went wrong, got {len(addresses)} addresses:")
        for address in addresses:
            print(f"address {address}")
        return

    address = addresses.pop()

    if not address:
        print("Unable to get IP address")
        return

    print(f"IP address consensus: {address}")

    dns_tasks = [asyncio.create_task(updater.set_dns_record(address)) for updater in updaters]
    await asyncio.gather(*dns_tasks)


def load_config():
    yaml = YAML(typ="safe")

    with open("config.yaml", "r") as config_file:
        config = yaml.load(config_file)

    providers = []
    for provider in config["providers"]:
        provider_class = get_provider_class(provider["type"])
        provider_params = provider.get("params", None)

        if provider_params:
            providers.append(provider_class(**provider_params))
        else:
            providers.append(provider_class())

    updaters = []
    for updater in config["updaters"]:
        updater_class = get_updater_class(updater["type"])
        updater_params = updater.get("params", None)
        updaters.append(updater_class(**updater_params))

    return providers, updaters


async def main():
    load_dotenv()

    app = web.Application()
    app.add_routes([
        web.get("/ip", handle),
    ])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    perform_self_check.start()
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    asyncio.run(main())
