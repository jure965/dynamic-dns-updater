import asyncio

import providers.ip
import providers.dns
from dotenv import load_dotenv


ip_providers = providers.ip.all_providers

dns_providers = providers.dns.all_providers


async def perform_check():
    ip_tasks = [asyncio.create_task(provider.get_ip_address()) for provider in ip_providers]
    addresses = set(await asyncio.gather(*ip_tasks))

    if len(addresses) != 1:
        print(f"something went wrong, got {len(addresses)} addresses:")
        for address in addresses:
            print(f"address {address}")
        return

    address = addresses.pop()

    if not address:
        print("no address found")
        return

    print(f"got address: {address}")

    dns_tasks = [asyncio.create_task(provider.set_dns_record(address)) for provider in dns_providers]
    await asyncio.gather(*dns_tasks)


async def main():
    load_dotenv()
    print("Hello from dynamic-dns-updater!")
    await perform_check()


if __name__ == "__main__":
    asyncio.run(main())
