from cloudflare import Cloudflare
from ipaddress import ip_address


class BaseDNSUpdater:
    def __init__(self, zone_name: str, record_type: str, record_name: str):
        self.zone_name = zone_name
        self.record_type = record_type
        self.record_name = record_name

    async def set_dns_record(self, ip):
        raise NotImplementedError


class CloudflareDNSUpdater(BaseDNSUpdater):
    async def set_dns_record(self, ip):
        client = Cloudflare()

        try:
            zone = client.zones.list(name=self.zone_name).result.pop()
        except IndexError as e:
            print(e)
            return

        try:
            record = client.dns.records.list(zone_id=zone.id, type=self.record_type, name=self.record_name).result.pop()
        except IndexError as e:
            print(e)
            return

        existing_ip = ip_address(record.content)

        if existing_ip == ip:
            print(f"No change needed for Cloudflare record {record.type} {record.name} {record.content}")
            return

        client.dns.records.edit(dns_record_id=record.id, zone_id=zone.id, type=self.record_type, name=self.record_name, content=str(ip))
        print(f"Cloudflare record {record.type} {record.name} {record.content} changed content to {ip}")
