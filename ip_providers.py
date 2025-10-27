import logging

from aiohttp import ClientSession
from ipaddress import IPv4Address, IPv6Address, ip_address


logger = logging.getLogger(__name__)


class UnknownIPProviderException(Exception):
    def __init__(self, provider_type):
        super().__init__(f"Unknown provider type '{provider_type}'")


def get_provider_class(provider_type):
    match provider_type:
        case "plain":
            return PlainIPProvider
    raise UnknownIPProviderException(provider_type)


class PlainIPProvider:
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password

    async def get_ip_address(self) -> IPv4Address | IPv6Address:
        auth = None
        if self.username and self.password:
            auth=(self.username, self.password)

        async with ClientSession(timeout=5) as session:
            async with session.get(self.url, auth=auth) as response:
                response_body = await response.text()

        address = None

        try:
            address = ip_address(response_body)
        except ValueError as e:
            logger.error(e)

        logger.info(f"{type(self).__name__} ({self.url}) returned '{address}'")

        return address
