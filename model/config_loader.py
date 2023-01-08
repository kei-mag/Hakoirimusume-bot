"""Provide Hakoirimusume's config value

The script first attempts to import `tomllib` (standard library available in Python 3.11 and later),
and if that fails, uses the `tomli` library.
"""

import os
from pprint import pprint

try:
    # For Python 3.11 or later
    from tomllib import TOMLDecodeError, load
except ImportError:
    # For Python 3.10 or earlier
    from tomli import TOMLDecodeError, load


class ConfigLoader:
    """Load Hakoirimusume config from TOML file.

    This class is singleton. So only 1 instance always exist.

    Example
    -------
    ```python
    config_dict: dict[str, Any] = ConfigLoader().config
    ```
    """

    CONFIG_FILE_PATH = 'config.toml'

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # ###### Default config value ######
        default_config = {
            "General": {
                "port": 21212,
                "data_dir": "data/",
                "database_name": "database.db"
            },
            "Hakoirimusume": {
                "initial_aikotoba": "aikotoba"
            }
        }
        ####################################
        if not self._load(self.CONFIG_FILE_PATH):
            print("Default configuration value will be used.")
            self.config = default_config

    def reload(self, filepath: str) -> None:
        """Reload config file

        Parameters
        ----------
        filepath : str
            File path of config file

            `config_loader.CONFIG_FILE_PATH` is specified, reload same file.
        """
        print("Reloading config file...")
        if not self._load(filepath):
            print("Config will not change.")

    def _load(self, filepath: str) -> bool:
        """Load TOML file

        Parameters
        ----------
        filepath : str
            TOML file path

        Returns
        -------
        bool
            `True`: Loaded successfully.
            `False`: Failed to load.
        """
        self.CONFIG_FILE_PATH = os.path.abspath(filepath)
        try:
            with open(file=self.CONFIG_FILE_PATH, mode='rb') as f:
                self.config = load(f)
        except FileNotFoundError as error:
            print("Error has occurred while loading config file.")
            print(error)
            return False
        except TOMLDecodeError as error:
            print("Error has occurred while parsing config file.")
            print(error)
            return False
        else:
            print(
                f"Config file \'{self.CONFIG_FILE_PATH}\' is loaded successfully.")
            print("--------------- Config ---------------")
            pprint(self.config, width=1)
            print("--------------------------------------")
            return True


if __name__ == '__main__':
    config = ConfigLoader().config
    print(config)
