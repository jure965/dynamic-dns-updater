import os

from dotenv import load_dotenv
from ruamel.yaml import YAML

from dns_updaters import get_updater_class
from ip_providers import get_provider_class


class Config:
    def __init__(self):
        self.providers = []
        self.updaters = []
        self.jwt_key = os.getenv("JWT_KEY")
        self.log_level = os.getenv("LOG_LEVEL", "WARNING")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8080"))
        self.self_check_url = os.getenv("SELF_CHECK_URL", f"http://{self.api_host}:{self.api_port}/check")


def load_config(path="config.yaml"):
    global config

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
    config.providers = providers

    updaters = []
    for updater in config_dict.get("updaters", list()):
        updater_class = get_updater_class(updater["type"])
        updater_params = updater.get("params", None)
        updaters.append(updater_class(**updater_params))
    config.updaters = updaters

load_dotenv()
config = Config()
