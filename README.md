# dynamic-dns-updater

External IP address checker and DNS updater.

Retrieve external IP addresses from multiple providers and update DNS records.

When using only one provider, make sure it is trusted. Multiple providers increase the chances that returned external
IP address is correct. Tool compares the returned IP addresses and performs the update only if they are all the same.

## ToDo

- refactor to async
- add scheduler
- containerize
- add docker compose file
