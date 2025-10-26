from providers.ip import ipify, ipinfo


ip_providers = [
    ipify,
    ipinfo,
]


def perform_check():
    addresses = [provider.get_ip_address() for provider in ip_providers]

    for address in addresses:
        print(address)


def main():
    print("Hello from dynamic-dns-updater!")
    perform_check()


if __name__ == "__main__":
    main()
