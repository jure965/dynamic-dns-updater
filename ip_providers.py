import requests
from ipaddress import IPv4Address, IPv6Address, ip_address


class UnknownIPProviderException(Exception):
    def __init__(self, provider_name):
        super().__init__(f"Unknown provider '{provider_name}'")


def get_provider_class(provider_name):
    match provider_name:
        case "ipify":
            return IPIfyIPProvider
        case "ipinfo":
            return IPInfoIPProvider
        case "generic":
            return GenericIPProvider
    raise UnknownIPProviderException(provider_name)


class BaseIPProvider:
    def __init__(self, url):
        self.url = url

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        raise NotImplementedError()


class GenericIPProvider(BaseIPProvider):
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

        print(f"{type(self).__name__} returned address {address} from {self.url}")

        return address


class IPInfoIPProvider(GenericIPProvider):
    def __init__(self):
        super().__init__("https://ipinfo.io/ip")


class IPIfyIPProvider(GenericIPProvider):
    def __init__(self):
        super().__init__("https://api.ipify.org")
