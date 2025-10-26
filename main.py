import asyncio
import os

from dotenv import load_dotenv

from providers.ip import IPIfyIPProvider, IPInfoIPProvider
from providers.dns import CloudflareDNSUpdater


async def perform_check():
    ip_providers = [
        IPIfyIPProvider(),
        IPInfoIPProvider(),
    ]

    zone_name = os.environ.get("CLOUDFLARE_ZONE_NAME")
    record_type = os.environ.get("CLOUDFLARE_RECORD_TYPE")
    record_name = os.environ.get("CLOUDFLARE_RECORD_NAME")

    dns_updaters = [
        CloudflareDNSUpdater(zone_name, record_type, record_name),
    ]

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

    dns_tasks = [asyncio.create_task(updater.set_dns_record(address)) for updater in dns_updaters]
    await asyncio.gather(*dns_tasks)


async def main():
    load_dotenv()
    print("Hello from dynamic-dns-updater!")
    await perform_check()


if __name__ == "__main__":
    asyncio.run(main())
