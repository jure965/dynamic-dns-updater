import providers.ip
import providers.dns
from dotenv import load_dotenv


ip_providers = providers.ip.all_providers

dns_providers = providers.dns.all_providers


def perform_check():
    addresses = set([provider.get_ip_address() for provider in ip_providers])

    if len(addresses) != 1:
        print(f"something went wrong, got {len(addresses)} addresses:")
        for address in addresses:
            print(f"address {address}")
        return

    address = addresses.pop()
    print(f"got address: {address}")

    for provider in dns_providers:
        provider.set_dns_record(address)


def main():
    load_dotenv()
    print("Hello from dynamic-dns-updater!")
    perform_check()


if __name__ == "__main__":
    main()
