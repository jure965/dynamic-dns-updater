# dynamic-dns-updater

External IP address checker and DNS updater.

Retrieve external IP addresses from multiple providers and update DNS records.

When using only one provider, make sure it is trusted. Multiple providers increase the chances that returned external
IP address is correct. Tool compares the returned IP addresses and performs the update only if they are all the same.

## Configuration

Environment variables for provider api tokens:

- CLOUDFLARE_API_TOKEN

Create `config.yaml` file from [config.example.yaml](config.example.yaml):

```yaml
# config.yaml

# specify a list of ip providers
providers:
  - type: plain
    params:
      url: https://ipecho.net/plain

# specify a list of dns updaters
updaters:
  - type: cloudflare
    params:
      zone_name: example.com
      record_type: A
      record_name: example.com
```


## ToDo

- add proper logging
- add scheduler
- containerize
- add docker compose file
- add self check api
- add ip echo api
