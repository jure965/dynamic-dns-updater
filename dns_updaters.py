import asyncio
import logging

from cloudflare import Cloudflare
from ipaddress import ip_address

from config import config

logger = logging.getLogger(__name__)


class UnknownDNSUpdaterException(Exception):
    def __init__(self, updater_type):
        super().__init__(f"Unknown updater type '{updater_type}'")


def get_updater_class(updater_type):
    match updater_type:
        case "cloudflare":
            return CloudflareDNSUpdater
    raise UnknownDNSUpdaterException(updater_type)


def init_updaters(updater_list):
    updaters = []

    for updater in updater_list:
        updater_class = get_updater_class(updater["type"])
        updater_params = updater.get("params", None)
        updaters.append(updater_class(**updater_params))

    config.updaters = updaters


class BaseDNSUpdater:
    def __init__(self, zone_name, record_type, record_name):
        self.zone_name = zone_name
        self.record_type = record_type
        self.record_name = record_name

    async def set_dns_record(self, new_ip):
        raise NotImplementedError


class CloudflareDNSUpdater(BaseDNSUpdater):
    async def set_dns_record(self, new_ip):
        client = Cloudflare()

        try:
            zone = await client.zones.list(name=self.zone_name).result.pop()
            record = await client.dns.records.list(
                zone_id=zone.id,
                type=self.record_type,
                name=self.record_name,
            ).result.pop()
        except IndexError as e:
            logger.error(e)
            return

        if ip_address(record.content) == new_ip:
            logger.info(f"{type(self).__name__} {record.type} {record.name} {record.content} left unchanged")
            return

        record = await client.dns.records.edit(
            dns_record_id=record.id,
            zone_id=zone.id,
            type=self.record_type,
            name=self.record_name,
            content=str(new_ip),
        )
        logger.info(f"{type(self).__name__} {record.type} {record.name} {record.content} updated to {new_ip}")


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
