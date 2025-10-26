import os

from cloudflare import Cloudflare
from ipaddress import ip_address


async def set_dns_record(ip):
    zone_name = os.environ.get("CLOUDFLARE_ZONE_NAME")
    record_type = os.environ.get("CLOUDFLARE_RECORD_TYPE")
    record_name = os.environ.get("CLOUDFLARE_RECORD_NAME")
    client = Cloudflare()

    try:
        zone = client.zones.list(name=zone_name).result.pop()
    except IndexError as e:
        print(e)
        return

    try:
        record = client.dns.records.list(zone_id=zone.id, type=record_type, name=record_name).result.pop()
    except IndexError as e:
        print(e)
        return

    existing_ip = ip_address(record.content)

    if existing_ip == ip:
        print(f"No change needed for Cloudflare record {record.type} {record.name} {record.content}")
        return

    client.dns.records.edit(dns_record_id=record.id, zone_id=zone.id, type=record_type, name=record_name, content=str(ip))
    print(f"Cloudflare record {record.type} {record.name} {record.content} changed content to {ip}")
