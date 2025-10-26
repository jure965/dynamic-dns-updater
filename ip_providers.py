import requests
from ipaddress import IPv4Address, IPv6Address, ip_address


class UnknownIPProviderException(Exception):
    def __init__(self, provider_type):
        super().__init__(f"Unknown provider type '{provider_type}'")


def get_provider_class(provider_type):
    match provider_type:
        case "plain":
            return PlainIPProvider
    raise UnknownIPProviderException(provider_type)


class BaseIPProvider:
    def __init__(self, url):
        self.url = url

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        raise NotImplementedError()


class PlainIPProvider(BaseIPProvider):
    """
    Basic GET request to a URL and a simple text response with IP address.
    """

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        response = requests.get(self.url)
        address = None

        try:
            address = ip_address(response.text)
        except ValueError as e:
            print(e)

        print(f"{type(self).__name__} ({self.url}) returned address {address}")

        return address
