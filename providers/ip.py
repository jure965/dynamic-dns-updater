import requests
from ipaddress import IPv4Address, IPv6Address, ip_address


class BaseIPProvider:
    def __init__(self, url):
        self.url = url

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        response = requests.get(self.url)
        address = None

        try:
            address = ip_address(response.text)
        except ValueError as e:
            print(e)

        return address


class GenericIPProvider(BaseIPProvider):
    pass


class IPInfoIPProvider(GenericIPProvider):
    def __init__(self):
        super().__init__("https://ipinfo.io/ip")


class IPIfyIPProvider(GenericIPProvider):
    def __init__(self):
        super().__init__("https://api.ipify.org")
