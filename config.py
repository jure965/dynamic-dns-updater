import os

from dotenv import load_dotenv
from ruamel.yaml import YAML

from dns_updaters import get_updater_class
from ip_providers import get_provider_class


class Config:
    def __init__(self, providers, updaters):
        self.providers = providers
        self.updaters = updaters
        self.secret = os.getenv("JWT_SECRET")
        self.log_level = os.getenv("LOG_LEVEL", "WARNING")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8080"))
        self.self_check_url = os.getenv("SELF_CHECK_URL", f"http://{self.api_host}:{self.api_port}/check")


config = Config([], [])


def load_config(path="config.yaml"):
    load_dotenv()

    yaml = YAML(typ="safe")

    with open(path, "r") as config_file:
        config_dict = yaml.load(config_file)

    providers = []
    for provider in config_dict.get("providers", list()):
        provider_class = get_provider_class(provider.get("type", "plain"))
        provider_params = provider.get("params", None)

        if provider_params:
            providers.append(provider_class(**provider_params))
        else:
            providers.append(provider_class())

    updaters = []
    for updater in config_dict.get("updaters", list()):
        updater_class = get_updater_class(updater["type"])
        updater_params = updater.get("params", None)
        updaters.append(updater_class(**updater_params))

    global config
    config = Config(providers, updaters)
