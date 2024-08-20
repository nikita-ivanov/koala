import json
from dataclasses import dataclass

CONFIG_PATH = "./app_config.json"  # loaded from home.py

@dataclass
class Configuration:
    hist_returns_path: str
    translator_model_path: str
    de_tokenizer_path: str
    en_tokenizer_path: str

def load_config() -> Configuration:
    try:
        with open(CONFIG_PATH) as file:
            json_config = json.load(file)

            return Configuration(hist_returns_path=json_config["hist_returns_path"],
                                 translator_model_path=json_config["translator_model_path"],
                                 de_tokenizer_path=json_config["de_tokenizer_path"],
                                 en_tokenizer_path=json_config["en_tokenizer_path"])
    except (FileNotFoundError, KeyError) as e:
        msg = "There was an error loading configuration file"
        raise RuntimeError(msg) from e
