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
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password

    def _send_request(self):
        if self.username and self.password:
            return requests.get(self.url, auth=(self.username, self.password))
        else:
            return requests.get(self.url)

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        raise NotImplementedError()


class PlainIPProvider(BaseIPProvider):
    """
    Basic GET request to a URL and a simple text response with IP address.
    """

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        response = self._send_request()
        address = None

        try:
            address = ip_address(response.text)
        except ValueError as e:
            print(e)

        print(f"{type(self).__name__} ({self.url}) returned address {address}")

        return address
