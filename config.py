import logging
import os
import sys

from dotenv import load_dotenv
from json_log_formatter import VerboseJSONFormatter
from ruamel.yaml import YAML

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.providers = []
        self.updaters = []
        self.jwt_key = os.getenv("JWT_KEY")
        self.log_level = os.getenv("LOG_LEVEL", "WARNING")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8080"))
        self.self_check_url = os.getenv("SELF_CHECK_URL", f"http://{self.api_host}:{self.api_port}/check")


def configure_logging():
    log_level = logging.getLevelName(config.log_level)
    formatter = VerboseJSONFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.root.addHandler(handler)
    logger.root.setLevel(log_level)


def load_config(path="config.yaml"):
    yaml = YAML(typ="safe")

    with open(path, "r") as config_file:
        config_dict = yaml.load(config_file)

    return config_dict.get("providers", list()), config_dict.get("updaters", list())


load_dotenv()
config = Config()
