import requests
from ipaddress import IPv4Address, IPv6Address, ip_address


async def get_ip_address() -> IPv4Address | IPv6Address:
    response = requests.get("https://ipinfo.io/ip")
    return ip_address(response.text)
