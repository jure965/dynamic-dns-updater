import logging

from cloudflare import Cloudflare
from ipaddress import ip_address


logger = logging.getLogger(__name__)


class UnknownDNSUpdaterException(Exception):
    def __init__(self, updater_type):
        super().__init__(f"Unknown updater type '{updater_type}'")


def get_updater_class(updater_type):
    match updater_type:
        case "cloudflare":
            return CloudflareDNSUpdater
    raise UnknownDNSUpdaterException(updater_type)


class BaseDNSUpdater:
    def __init__(self, zone_name: str, record_type: str, record_name: str):
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
            record = await client.dns.records.list(zone_id=zone.id, type=self.record_type, name=self.record_name).result.pop()
        except IndexError as e:
            logger.error(e)
            return

        if ip_address(record.content) == new_ip:
            logger.info(f"{type(self).__name__} record {record.type} {record.name} {record.content} left unchanged")
            return

        record = await client.dns.records.edit(dns_record_id=record.id, zone_id=zone.id, type=self.record_type, name=self.record_name, content=str(new_ip))
        logger.info(f"{type(self).__name__} record {record.type} {record.name} {record.content} changed content to {new_ip}")
