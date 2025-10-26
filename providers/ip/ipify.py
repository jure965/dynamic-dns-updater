import requests
from ipaddress import IPv4Address, IPv6Address, ip_address


async def get_ip_address() -> IPv4Address | IPv6Address:
    response = requests.get("https://api.ipify.org")
    address = None

    try:
        address = ip_address(response.text)
    except ValueError as e:
        print(e)

    return address
