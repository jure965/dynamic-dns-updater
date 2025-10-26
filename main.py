import asyncio

from dotenv import load_dotenv
from ruamel.yaml import YAML

from dns_updaters import get_updater_class
from ip_providers import get_provider_class


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
    providers, updaters = load_config()
    print("Hello from dynamic-dns-updater!")
    await perform_check(providers, updaters)


if __name__ == "__main__":
    asyncio.run(main())
